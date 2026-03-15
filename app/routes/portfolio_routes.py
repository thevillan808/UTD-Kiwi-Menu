from flask import Blueprint, g, jsonify, request
from pydantic import ValidationError

import app.service.access_service as access_service
import app.service.portfolio_service as portfolio_service
import app.service.transaction_service as transaction_service
import app.service.user_service as user_service
from app.auth import require_auth
from app.db import db
from app.schemas import CreatePortfolioRequest, GrantAccessRequest

portfolio_bp = Blueprint('portfolio', __name__)


@portfolio_bp.route('/', methods=['GET'])
@require_auth
def get_all_portfolios():
    portfolios = portfolio_service.get_all_portfolios()
    return jsonify([portfolio.__to_dict__() for portfolio in portfolios]), 200


@portfolio_bp.route('/<int:portfolio_id>', methods=['GET'])
@require_auth
def get_portfolio(portfolio_id):
    portfolio = portfolio_service.get_portfolio_by_id(portfolio_id)
    if portfolio is None:
        return jsonify({'error': 'Not Found', 'detail': f'Portfolio {portfolio_id} not found'}), 404
    current_user = g.current_user
    if portfolio.owner != current_user and not access_service.can_view(portfolio_id, current_user):
        return jsonify({'error': 'Forbidden'}), 403
    return jsonify(portfolio.__to_dict__()), 200


@portfolio_bp.route('/user/<username>', methods=['GET'])
@require_auth
def get_portfolios_by_user(username):
    user = user_service.get_user_by_username(username)
    if user is None:
        return jsonify({'error': 'Not Found', 'detail': f'User {username} not found'}), 404
    portfolios = portfolio_service.get_portfolios_by_user(user)
    return jsonify([portfolio.__to_dict__() for portfolio in portfolios]), 200


@portfolio_bp.route('/', methods=['POST'])
@require_auth
def create_portfolio():
    req_data = CreatePortfolioRequest.model_validate(request.get_json())
    current_user = g.current_user
    # only the owner can create portfolios for themselves
    if req_data.username != current_user:
        return jsonify({'error': 'Forbidden'}), 403
    user = user_service.get_user_by_username(req_data.username)
    if user is None:
        return jsonify({'error': 'Not Found', 'detail': f'User {req_data.username} not found'}), 404
    portfolio_id = portfolio_service.create_portfolio(
        name=req_data.name,
        description=req_data.description,
        user=user,
    )
    db.session.commit()
    return jsonify({'message': 'Portfolio created successfully', 'portfolio_id': portfolio_id}), 201


@portfolio_bp.route('/<int:portfolio_id>', methods=['DELETE'])
@require_auth
def delete_portfolio(portfolio_id):
    portfolio = portfolio_service.get_portfolio_by_id(portfolio_id)
    if portfolio is None:
        return jsonify({'error': 'Not Found', 'detail': f'Portfolio {portfolio_id} not found'}), 404
    current_user = g.current_user
    if portfolio.owner != current_user:
        return jsonify({'error': 'Forbidden'}), 403
    portfolio_service.delete_portfolio(portfolio_id)
    db.session.commit()
    return jsonify({'message': 'Portfolio deleted successfully'}), 200


@portfolio_bp.route('/<int:portfolio_id>/transactions', methods=['GET'])
@require_auth
def get_portfolio_transactions(portfolio_id):
    portfolio = portfolio_service.get_portfolio_by_id(portfolio_id)
    if portfolio is None:
        return jsonify({'error': 'Not Found', 'detail': f'Portfolio {portfolio_id} not found'}), 404
    current_user = g.current_user
    if portfolio.owner != current_user and not access_service.can_view(portfolio_id, current_user):
        return jsonify({'error': 'Forbidden'}), 403
    transactions = transaction_service.get_transactions_by_portfolio_id(portfolio_id)
    return jsonify([transaction.__to_dict__() for transaction in transactions]), 200


@portfolio_bp.route('/<int:portfolio_id>/access', methods=['POST'])
@require_auth
def grant_access(portfolio_id):
    portfolio = portfolio_service.get_portfolio_by_id(portfolio_id)
    if portfolio is None:
        return jsonify({'error': 'Not Found', 'detail': f'Portfolio {portfolio_id} not found'}), 404
    current_user = g.current_user
    if portfolio.owner != current_user:
        return jsonify({'error': 'Forbidden', 'detail': 'Only the portfolio owner can grant access'}), 403
    req_data = GrantAccessRequest.model_validate(request.get_json())
    access_service.grant_access(portfolio_id, req_data.username, req_data.role)
    db.session.commit()
    return jsonify({'message': 'Access granted successfully'}), 201


@portfolio_bp.route('/<int:portfolio_id>/access/<username>', methods=['DELETE'])
@require_auth
def revoke_access(portfolio_id, username):
    portfolio = portfolio_service.get_portfolio_by_id(portfolio_id)
    if portfolio is None:
        return jsonify({'error': 'Not Found', 'detail': f'Portfolio {portfolio_id} not found'}), 404
    current_user = g.current_user
    if portfolio.owner != current_user:
        return jsonify({'error': 'Forbidden', 'detail': 'Only the portfolio owner can revoke access'}), 403
    access_service.revoke_access(portfolio_id, username)
    db.session.commit()
    return jsonify({'message': 'Access revoked successfully'}), 200
