from flask import Blueprint, g, jsonify, request

import app.service.access_service as access_service
import app.service.portfolio_service as portfolio_service
from app.auth import require_auth
from app.db import db
from app.schemas import BuyTradeRequest, SellTradeRequest
from app.service import trade_service

trade_bp = Blueprint('trade', __name__)


@trade_bp.route('/buy', methods=['POST'])
@require_auth
def execute_purchase_order():
    req_data = BuyTradeRequest.model_validate(request.get_json())
    current_user = g.current_user
    portfolio = portfolio_service.get_portfolio_by_id(req_data.portfolio_id)
    if portfolio is None:
        return jsonify({'error': 'Not Found', 'detail': f'Portfolio {req_data.portfolio_id} not found'}), 404
    if portfolio.owner != current_user and not access_service.can_manage(req_data.portfolio_id, current_user):
        return jsonify({'error': 'Forbidden'}), 403
    trade_service.execute_purchase_order(
        portfolio_id=req_data.portfolio_id,
        ticker=req_data.ticker,
        quantity=req_data.quantity,
    )
    db.session.commit()
    return jsonify({'message': 'Purchase order executed successfully'}), 201


@trade_bp.route('/sell', methods=['POST'])
@require_auth
def liquidate_investment():
    req_data = SellTradeRequest.model_validate(request.get_json())
    current_user = g.current_user
    portfolio = portfolio_service.get_portfolio_by_id(req_data.portfolio_id)
    if portfolio is None:
        return jsonify({'error': 'Not Found', 'detail': f'Portfolio {req_data.portfolio_id} not found'}), 404
    if portfolio.owner != current_user and not access_service.can_manage(req_data.portfolio_id, current_user):
        return jsonify({'error': 'Forbidden'}), 403
    trade_service.liquidate_investment(
        portfolio_id=req_data.portfolio_id,
        ticker=req_data.ticker,
        quantity=req_data.quantity,
    )
    db.session.commit()
    return jsonify({'message': 'Investment liquidated successfully'}), 200
