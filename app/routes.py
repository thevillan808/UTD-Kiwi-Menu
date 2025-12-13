from flask import Blueprint, request, jsonify
import logging
from .domain.User import User
import traceback
from .data_access import *

api = Blueprint('api', __name__)

@api.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Flask API is running',
        'version': '1.0'
    }), 200

@api.route('/users', methods=['GET'])
def get_users():
    try:
        users = query_all_users()
        return jsonify([u.__dict__ for u in users])
    except Exception as e:
        logging.error(f"Error getting users: {e}")
        return jsonify({'error': str(e)}), 500

@api.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Missing JSON body'}), 400
        
        user = User(
            data.get('username', ''),
            data.get('password', ''),
            data.get('first_name', ''),
            data.get('last_name', ''),
            data.get('balance', 0.0),
            data.get('role', 'user')
        )
        create_new_user(user)
        return jsonify({'message': 'User created'}), 201
    except Exception as e:
        logging.error(f"Error creating user: {e}")
        return jsonify({'error': str(e)}), 500

@api.route('/users/<username>', methods=['GET'])
def get_user_by_id(username):
    try:
        user = query_user(username)
        if not user:
            return jsonify({'error': f'User {username} not found'}), 404
        return jsonify(user.__dict__)
    except Exception as e:
        logging.error(f"Error getting user: {e}")
        return jsonify({'error': str(e)}), 500

@api.route('/users/<username>', methods=['DELETE'])
def delete_user_route(username):
    try:
        success = delete_user(username)
        if success:
            return jsonify({'message': f'User {username} deleted'}), 200
        return jsonify({'error': f'User {username} not found'}), 404
    except Exception as e:
        logging.error(f"Error deleting user: {e}")
        return jsonify({'error': str(e)}), 500

@api.route('/portfolios', methods=['GET'])
def get_portfolios():
    try:
        portfolios = query_all_portfolios()
        return jsonify([p.__dict__ for p in portfolios])
    except Exception as e:
        logging.error(f"Error getting portfolios: {e}")
        return jsonify({'error': str(e)}), 500

@api.route('/portfolios', methods=['POST'])
def create_portfolio_route():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Missing JSON body'}), 400
        
        p = create_portfolio(
            data.get('name', ''),
            data.get('description', ''),
            data.get('investment_strategy', ''),
            data.get('username', '')
        )
        return jsonify(p.__dict__), 201
    except Exception as e:
        logging.error(f"Error creating portfolio: {e}")
        return jsonify({'error': str(e)}), 500

@api.route('/portfolios/<int:portfolio_id>', methods=['GET'])
def get_portfolio_by_id(portfolio_id):
    try:
        portfolio = query_portfolio(portfolio_id)
        if not portfolio:
            return jsonify({'error': f'Portfolio {portfolio_id} not found'}), 404
        return jsonify(portfolio.__dict__)
    except Exception as e:
        logging.error(f"Error getting portfolio: {e}")
        return jsonify({'error': str(e)}), 500

@api.route('/portfolios/<int:portfolio_id>', methods=['DELETE'])
def delete_portfolio_route(portfolio_id):
    try:
        success = delete_portfolio(portfolio_id)
        if success:
            return jsonify({'message': f'Portfolio {portfolio_id} deleted'}), 200
        return jsonify({'error': f'Portfolio {portfolio_id} not found'}), 404
    except Exception as e:
        logging.error(f"Error deleting portfolio: {e}")
        return jsonify({'error': str(e)}), 500

@api.route('/portfolios/<int:portfolio_id>/securities', methods=['POST'])
def add_security_to_portfolio(portfolio_id):
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Missing JSON body'}), 400
        
        ticker = data.get('ticker', '').upper()
        quantity = data.get('quantity', 0)
        
        if not ticker or quantity <= 0:
            return jsonify({'error': 'ticker and positive quantity required'}), 400
        
        # Get current investment and update quantity
        current = get_investment(portfolio_id, ticker)
        new_quantity = (current.quantity if current else 0) + quantity
        
        success = update_investment(portfolio_id, ticker, new_quantity)
        if success:
            return jsonify({
                'message': f'Added {quantity} shares of {ticker} to portfolio {portfolio_id}',
                'ticker': ticker,
                'new_quantity': new_quantity
            }), 201
        return jsonify({'error': 'Failed to add security to portfolio'}), 500
    except Exception as e:
        logging.error(f"Error adding security: {e}")
        return jsonify({'error': str(e)}), 500

@api.route('/portfolios/<int:portfolio_id>/securities/<ticker>', methods=['DELETE'])
def harvest_investment(portfolio_id, ticker):
    try:
        ticker = ticker.upper()
        success = remove_investment(portfolio_id, ticker)
        if success:
            return jsonify({'message': f'Harvested {ticker} from portfolio {portfolio_id}'}), 200
        return jsonify({'error': f'Investment {ticker} not found in portfolio {portfolio_id}'}), 404
    except Exception as e:
        logging.error(f"Error harvesting investment: {e}")
        return jsonify({'error': str(e)}), 500

@api.route('/securities', methods=['GET'])
def get_securities():
    try:
        securities = query_all_securities()
        return jsonify([s.__dict__ for s in securities])
    except Exception as e:
        logging.error(f"Error getting securities: {e}")
        return jsonify({'error': str(e)}), 500

@api.route('/securities', methods=['POST'])
def create_security_route():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Missing JSON body'}), 400
        
        security = create_security(
            data.get('ticker', '').upper(),
            data.get('name', ''),
            data.get('asset_type', 'Stock')
        )
        return jsonify(security.__dict__), 201
    except Exception as e:
        logging.error(f"Error creating security: {e}")
        return jsonify({'error': str(e)}), 500

@api.route('/transactions/security/<ticker>', methods=['GET'])
def get_transactions_by_security(ticker):
    try:
        transactions = query_transactions_by_ticker(ticker.upper())
        return jsonify([t.__dict__ for t in transactions])
    except Exception as e:
        logging.error(f"Error getting transactions: {e}")
        return jsonify({'error': str(e)}), 500
