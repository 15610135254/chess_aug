from flask import Blueprint, request, jsonify
from chess_engine.board import ChessBoard
from chess_engine.rules import ChessRules
from chess_engine.ai_suggestion import AIChessSuggestionEngine
from api.validators import validate_move_request
import os

# 初始化AI引擎
ai_suggestion_engine = None

try:
    # 查找频率模型数据文件
    frequency_model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'data', 'move_frequency_analysis.json')
    
    if os.path.exists(frequency_model_path):
        print(f"加载AI建议引擎: {frequency_model_path}")
        ai_suggestion_engine = AIChessSuggestionEngine(frequency_model_path)
        print("AI建议引擎加载成功")
    else:
        print(f"频率模型文件不存在: {frequency_model_path}")
        
except Exception as e:
    print(f"AI引擎加载失败: {e}")

# 设置chess_ai为ai_suggestion_engine以保持兼容性
chess_ai = ai_suggestion_engine

api_bp = Blueprint('api', __name__)

@api_bp.route('/move', methods=['POST'])
def move_piece():
    try:
        # 验证请求数据
        data = request.get_json()
        validation_result = validate_move_request(data)
        if not validation_result['valid']:
            return jsonify({
                'status': 'error',
                'message': validation_result['message']
            }), 400
        
        board_string = data['board']
        move_string = data['move']
        
        # 解析移动操作
        if len(move_string) != 4:
            return jsonify({
                'status': 'error',
                'message': '移动格式错误'
            }), 400
        
        from_x = int(move_string[0])
        from_y = int(move_string[1])
        to_x = int(move_string[2])
        to_y = int(move_string[3])
        
        # 创建棋盘对象
        try:
            board = ChessBoard(board_string)
        except ValueError as e:
            return jsonify({
                'status': 'error',
                'message': f'棋盘状态无效: {str(e)}'
            }), 400

        # 验证移动是否合法
        validation_result = ChessRules.validate_move_with_reason(board, from_x, from_y, to_x, to_y)
        if not validation_result['valid']:
            return jsonify({
                'status': 'invalid',
                'message': validation_result['reason']
            })

        # 执行移动
        move_result = board.move_piece(from_x, from_y, to_x, to_y)
        if not move_result['success']:
            return jsonify({
                'status': 'error',
                'message': '移动失败：坐标超出范围或棋子不存在'
            })

        # 返回新的棋盘状态
        new_board_string = board.to_string()

        response_data = {
            'status': 'success',
            'board': new_board_string,
            'pieces': board.to_piece_list(),
            'message': '移动成功',
            'game_over': move_result['game_over'],
            'winner': move_result['winner']
        }

        # 如果游戏结束，更新消息
        if move_result['game_over']:
            winner_name = '红方' if move_result['winner'] == 'red' else '黑方'
            response_data['message'] = f'游戏结束！{winner_name}获胜！'

        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'服务器错误: {str(e)}'
        }), 500

@api_bp.route('/init', methods=['GET'])
def init_board():
    try:
        # 创建初始棋盘
        board = ChessBoard()
        board_string = board.to_string()
        
        return jsonify({
            'status': 'success',
            'board': board_string,
            'pieces': board.to_piece_list(),
            'message': '棋盘初始化成功'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'服务器错误: {str(e)}'
        }), 500

@api_bp.route('/validate', methods=['POST'])
def validate_move():
    try:
        # 验证请求数据
        data = request.get_json()
        validation_result = validate_move_request(data)
        if not validation_result['valid']:
            return jsonify({
                'status': 'error',
                'message': validation_result['message']
            }), 400
        
        board_string = data['board']
        move_string = data['move']
        
        # 解析移动操作
        if len(move_string) != 4:
            return jsonify({
                'status': 'error',
                'message': '移动格式错误'
            }), 400
        
        from_x = int(move_string[0])
        from_y = int(move_string[1])
        to_x = int(move_string[2])
        to_y = int(move_string[3])
        
        # 创建棋盘对象
        try:
            board = ChessBoard(board_string)
        except ValueError as e:
            return jsonify({
                'status': 'error',
                'message': f'棋盘状态无效: {str(e)}'
            }), 400
        
        # 验证移动是否合法
        is_valid = ChessRules.is_valid_move(board, from_x, from_y, to_x, to_y)
        
        return jsonify({
            'status': 'success',
            'valid': is_valid,
            'message': '验证完成'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'服务器错误: {str(e)}'
        }), 500

@api_bp.route('/ai/suggest', methods=['POST'])
def suggest_move():
    """AI走法推荐接口"""
    try:
        if ai_suggestion_engine is None:
            return jsonify({
                'status': 'error',
                'message': 'AI模块未加载'
            }), 503
        
        # 验证请求数据
        data = request.get_json()
        if not data or 'board' not in data:
            return jsonify({
                'status': 'error',
                'message': '缺少必要参数: board'
            }), 400
        
        board_string = data['board']
        side = data.get('side', 'red')  # 默认红方
        
        # 验证棋盘状态
        try:
            board = ChessBoard(board_string)
        except ValueError as e:
            return jsonify({
                'status': 'error',
                'message': f'棋盘状态无效: {str(e)}'
            }), 400
        
        # 获取AI建议
        suggestions_result = ai_suggestion_engine.get_ai_suggestions(board_string, side, top_k=3)
        
        if suggestions_result['status'] != 'success':
            return jsonify({
                'status': 'error',
                'message': suggestions_result['message']
            })
        
        suggestions = suggestions_result['suggestions']
        suggested_move = suggestions[0]['move'] if suggestions else None
        
        if not suggested_move:
            return jsonify({
                'status': 'error',
                'message': '无法生成走法建议'
            })
        
        # 准备响应数据
        response_data = {
            'status': 'success',
            'suggested_move': suggested_move,
            'suggestions': suggestions,
            'message': 'AI推荐完成'
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'服务器错误: {str(e)}'
        }), 500

@api_bp.route('/ai/info', methods=['GET'])
def ai_info():
    """获取AI模型信息"""
    try:
        if ai_suggestion_engine is None:
            return jsonify({
                'status': 'error',
                'message': 'AI模块未加载'
            }), 503
        
        model_info = ai_suggestion_engine.get_engine_info()
        
        return jsonify({
            'status': 'success',
            'model_info': model_info,
            'message': 'AI信息获取成功'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'服务器错误: {str(e)}'
        }), 500

@api_bp.route('/ai/frequency_recommend', methods=['POST'])
def frequency_recommend():
    """基于频率的走法推荐接口"""
    try:
        if ai_suggestion_engine is None:
            return jsonify({
                'status': 'error',
                'message': '频率推荐模型未加载'
            }), 503
        
        # 验证请求数据
        data = request.get_json()
        if not data or 'board' not in data:
            return jsonify({
                'status': 'error',
                'message': '缺少必要参数: board'
            }), 400
        
        board_state = data['board']
        side = data.get('side', 'red')  # 默认红方
        
        # 验证棋盘状态格式（支持64字符和180字符格式）
        if len(board_state) not in [64, 180] or not board_state.isdigit():
            return jsonify({
                'status': 'error',
                'message': '棋盘状态格式错误（应为64或180字符的数字字符串）'
            }), 400
        
        # 获取AI建议
        result = ai_suggestion_engine.get_ai_suggestions(board_state, side, top_k=3)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'频率推荐失败: {str(e)}'
        }), 500

@api_bp.route('/ai/analyze_position', methods=['POST'])
def analyze_position():
    """分析当前局面"""
    try:
        if ai_suggestion_engine is None:
            return jsonify({
                'status': 'error',
                'message': '频率推荐模型未加载'
            }), 503
        
        # 验证请求数据
        data = request.get_json()
        if not data or 'board' not in data:
            return jsonify({
                'status': 'error',
                'message': '缺少必要参数: board'
            }), 400
        
        board_state = data['board']
        
        # 验证棋盘状态格式（支持64字符和180字符格式）
        if len(board_state) not in [64, 180] or not board_state.isdigit():
            return jsonify({
                'status': 'error',
                'message': '棋盘状态格式错误（应为64或180字符的数字字符串）'
            }), 400
        
        # 分析局面
        analysis = ai_suggestion_engine.get_board_analysis(board_state)
        
        return jsonify({
            'status': 'success',
            'analysis': analysis,
            'message': '局面分析完成'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'局面分析失败: {str(e)}'
        }), 500

@api_bp.route('/ai/black_auto_move', methods=['POST'])
def black_auto_move():
    """黑棋自动移动接口"""
    try:
        if ai_suggestion_engine is None:
            return jsonify({
                'status': 'error',
                'message': 'AI建议引擎未加载'
            }), 503
        
        # 验证请求数据
        data = request.get_json()
        if not data or 'board' not in data:
            return jsonify({
                'status': 'error',
                'message': '缺少必要参数: board'
            }), 400
        
        board_state = data['board']
        
        # 验证棋盘状态格式（支持64字符和180字符格式）
        if len(board_state) not in [64, 180] or not board_state.isdigit():
            return jsonify({
                'status': 'error',
                'message': '棋盘状态格式错误（应为64或180字符的数字字符串）'
            }), 400
        
        # 执行AI移动
        result = ai_suggestion_engine.execute_ai_move(board_state, 'black')
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'黑棋自动移动失败: {str(e)}'
        }), 500

@api_bp.route('/ai/get_suggestions', methods=['POST'])
def get_ai_suggestions():
    """获取AI移动建议接口"""
    try:
        if ai_suggestion_engine is None:
            return jsonify({
                'status': 'error',
                'message': 'AI建议引擎未加载'
            }), 503
        
        # 验证请求数据
        data = request.get_json()
        if not data or 'board' not in data:
            return jsonify({
                'status': 'error',
                'message': '缺少必要参数: board'
            }), 400
        
        board_state = data['board']
        player = data.get('player', 'red')  # 默认红方
        top_k = data.get('top_k', 3)  # 默认返回3个建议
        
        # 获取AI建议
        result = ai_suggestion_engine.get_ai_suggestions(board_state, player, top_k)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'获取AI建议失败: {str(e)}'
        }), 500

@api_bp.route('/ai/execute_move', methods=['POST'])
def execute_ai_move():
    """执行AI移动并返回新棋盘状态"""
    try:
        if ai_suggestion_engine is None:
            return jsonify({
                'status': 'error',
                'message': 'AI建议引擎未加载'
            }), 503
        
        # 验证请求数据
        data = request.get_json()
        if not data or 'board' not in data:
            return jsonify({
                'status': 'error',
                'message': '缺少必要参数: board'
            }), 400
        
        board_state = data['board']
        player = data.get('player', 'black')  # 默认黑方自动移动
        
        # 执行AI移动
        result = ai_suggestion_engine.execute_ai_move(board_state, player)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'执行AI移动失败: {str(e)}'
        }), 500

@api_bp.route('/ai/compare_boards', methods=['POST'])
def compare_board_states():
    """对比棋盘状态接口"""
    try:
        if ai_suggestion_engine is None:
            return jsonify({
                'status': 'error',
                'message': 'AI建议引擎未加载'
            }), 503
        
        # 验证请求数据
        data = request.get_json()
        if not data or 'frontend_board' not in data or 'target_board' not in data:
            return jsonify({
                'status': 'error',
                'message': '缺少必要参数: frontend_board, target_board'
            }), 400
        
        frontend_board = data['frontend_board']
        target_board = data['target_board']
        
        # 对比棋盘状态
        result = ai_suggestion_engine.compare_board_states(frontend_board, target_board)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'对比棋盘状态失败: {str(e)}'
        }), 500

@api_bp.route('/ai/analyze_board', methods=['POST'])
def analyze_board():
    """分析棋盘状态接口"""
    try:
        if ai_suggestion_engine is None:
            return jsonify({
                'status': 'error',
                'message': 'AI建议引擎未加载'
            }), 503
        
        # 验证请求数据
        data = request.get_json()
        if not data or 'board' not in data:
            return jsonify({
                'status': 'error',
                'message': '缺少必要参数: board'
            }), 400
        
        board_state = data['board']
        
        # 分析棋盘状态
        result = ai_suggestion_engine.get_board_analysis(board_state)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'分析棋盘状态失败: {str(e)}'
        }), 500

@api_bp.route('/ai/engine_info', methods=['GET'])
def get_engine_info():
    """获取AI引擎信息"""
    try:
        if ai_suggestion_engine is None:
            return jsonify({
                'status': 'error',
                'message': 'AI建议引擎未加载'
            }), 503
        
        # 获取引擎信息
        result = ai_suggestion_engine.get_engine_info()
        
        return jsonify({
            'status': 'success',
            'engine_info': result
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'获取引擎信息失败: {str(e)}'
        }), 500
