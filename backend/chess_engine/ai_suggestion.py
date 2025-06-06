"""
AI建议引擎 - 基于频率数据提供棋步建议
对比前端棋盘状态与频率数据，返回最佳移动建议
"""

import json
import os
from typing import List, Dict, Optional, Tuple
from .board import ChessBoard


class AIChessSuggestionEngine:
    def __init__(self, frequency_data_path: str):
        """
        初始化AI建议引擎
        
        Args:
            frequency_data_path: 频率数据文件路径
        """
        self.frequency_data = []
        self.board_move_map = {}  # board_state -> [(player, move, frequency), ...]
        self.load_frequency_data(frequency_data_path)
    
    def load_frequency_data(self, data_path: str):
        """加载频率数据并建立索引"""
        try:
            if not os.path.exists(data_path):
                print(f"警告: 频率数据文件不存在: {data_path}")
                return
                
            with open(data_path, 'r', encoding='utf-8') as f:
                self.frequency_data = json.load(f)
            
            # 建立棋盘状态到移动的映射索引
            for entry in self.frequency_data:
                board_state = entry.get('board', '')
                player = entry.get('player', '')
                move = entry.get('move', '')
                frequency = entry.get('frequency', 0)
                
                if board_state not in self.board_move_map:
                    self.board_move_map[board_state] = []
                
                self.board_move_map[board_state].append({
                    'player': player,
                    'move': move,
                    'frequency': frequency
                })
            
            # 按频率排序每个棋盘状态的移动选项
            for board_state in self.board_move_map:
                self.board_move_map[board_state].sort(key=lambda x: x['frequency'], reverse=True)
            
            print(f"AI建议引擎加载成功，包含 {len(self.frequency_data)} 条记录，{len(self.board_move_map)} 个不同棋盘状态")
            
        except Exception as e:
            print(f"加载频率数据失败: {e}")
            self.frequency_data = []
            self.board_move_map = {}
    
    def get_ai_suggestions(self, board_state: str, player: str = 'red', top_k: int = 3) -> Dict:
        """
        获取AI移动建议

        Args:
            board_state: 180字符的棋盘状态字符串（与spark_chess_analysis.py兼容）
            player: 玩家方 ('red' 或 'black')
            top_k: 返回前k个建议

        Returns:
            dict: AI建议结果
        """
        # 验证棋盘状态格式
        if not self._validate_board_state(board_state):
            return {
                'status': 'error',
                'message': '棋盘状态格式无效',
                'suggestions': []
            }

        # 查找匹配的棋盘状态
        if board_state not in self.board_move_map:
            # 尝试找到最相似的棋盘状态
            similar_result = self._find_most_similar_board_state(board_state, player, top_k)
            if similar_result['status'] == 'success':
                return similar_result
            else:
                return {
                    'status': 'no_match',
                    'message': '当前棋盘状态在历史数据中未找到，也无法找到相似状态',
                    'suggestions': []
                }
        
        # 获取该棋盘状态下指定玩家的所有移动
        all_moves = self.board_move_map[board_state]
        player_moves = [move for move in all_moves if move['player'] == player]
        
        if not player_moves:
            return {
                'status': 'no_player_moves',
                'message': f'该棋盘状态下没有找到{player}方的移动记录',
                'suggestions': []
            }
        
        # 取前k个高频移动
        top_moves = player_moves[:top_k]
        
        suggestions = []
        for move_data in top_moves:
            move = move_data['move']
            frequency = move_data['frequency']

            # 验证移动格式
            if self._validate_move_format(move):
                # 验证走法在当前棋盘状态下是否有效
                if self._validate_move_on_board(board_state, move, player):
                    suggestions.append({
                        'move': move,
                        'frequency': frequency,
                        'from_position': f"({move[0]},{move[1]})",
                        'to_position': f"({move[2]},{move[3]})",
                        'description': f"从({move[0]},{move[1]})移动到({move[2]},{move[3]})"
                    })
        
        # 如果没有有效的建议，尝试生成基于当前棋盘的合法走法
        if not suggestions:
            fallback_suggestions = self._generate_fallback_suggestions(board_state, player, top_k)
            if fallback_suggestions:
                return {
                    'status': 'success',
                    'message': f'基于当前棋盘生成{len(fallback_suggestions)}个建议（历史数据中无匹配走法）',
                    'board_state': board_state,
                    'player': player,
                    'suggestions': fallback_suggestions,
                    'total_moves_available': len(fallback_suggestions),
                    'fallback_mode': True
                }
            else:
                return {
                    'status': 'no_valid_moves',
                    'message': f'该棋盘状态下没有找到{player}方的有效移动',
                    'suggestions': []
                }

        return {
            'status': 'success',
            'message': f'找到{len(suggestions)}个AI建议',
            'board_state': board_state,
            'player': player,
            'suggestions': suggestions,
            'total_moves_available': len(player_moves)
        }
    
    def execute_ai_move(self, board_state: str, player: str = 'black') -> Dict:
        """
        执行AI推荐的最佳移动，返回新的棋盘状态
        
        Args:
            board_state: 当前棋盘状态
            player: 执行移动的玩家
            
        Returns:
            dict: 包含新棋盘状态和移动信息的结果
        """
        # 获取AI建议
        suggestion_result = self.get_ai_suggestions(board_state, player, top_k=1)
        
        if suggestion_result['status'] != 'success' or not suggestion_result['suggestions']:
            return {
                'status': 'failed',
                'message': '无法获取AI移动建议',
                'original_board': board_state,
                'new_board': board_state,
                'move_executed': None
            }
        
        best_move = suggestion_result['suggestions'][0]['move']
        
        try:
            print(f"DEBUG execute_ai_move: 开始执行AI移动，玩家={player}, 移动={best_move}")
            print(f"DEBUG execute_ai_move: 原始棋盘状态长度={len(board_state)}, 前50字符={board_state[:50]}")

            # 创建棋盘对象
            board = ChessBoard(board_state)

            # 解析移动
            from_x = int(best_move[0])
            from_y = int(best_move[1])
            to_x = int(best_move[2])
            to_y = int(best_move[3])

            print(f"DEBUG execute_ai_move: 移动坐标 从({from_x},{from_y}) 到({to_x},{to_y})")

            # 检查移动前的棋盘状态
            piece_at_from = board.get_piece_at(from_x, from_y)
            piece_at_to = board.get_piece_at(to_x, to_y)
            print(f"DEBUG execute_ai_move: 起始位置棋子={piece_at_from}, 目标位置棋子={piece_at_to}")

            # 验证移动是否合法（需要导入规则模块）
            from .rules import ChessRules
            validation_result = ChessRules.validate_move_with_reason(board, from_x, from_y, to_x, to_y)

            if not validation_result['valid']:
                return {
                    'status': 'invalid_move',
                    'message': f'AI建议的移动无效: {validation_result["reason"]}',
                    'original_board': board_state,
                    'new_board': board_state,
                    'move_executed': best_move,
                    'validation_error': validation_result['reason']
                }

            # 执行移动
            print(f"DEBUG execute_ai_move: 开始执行移动")
            move_result = board.move_piece(from_x, from_y, to_x, to_y)
            print(f"DEBUG execute_ai_move: 移动结果={move_result}")

            if not move_result['success']:
                return {
                    'status': 'execution_failed',
                    'message': '移动执行失败',
                    'original_board': board_state,
                    'new_board': board_state,
                    'move_executed': best_move
                }

            # 获取新的棋盘状态
            new_board_state = board.to_string()
            print(f"DEBUG execute_ai_move: 新棋盘状态长度={len(new_board_state)}, 前50字符={new_board_state[:50]}")

            return {
                'status': 'success',
                'message': f'{player}方AI移动完成',
                'original_board': board_state,
                'new_board': new_board_state,
                'move_executed': best_move,
                'move_description': suggestion_result['suggestions'][0]['description'],
                'frequency': suggestion_result['suggestions'][0]['frequency'],
                'game_over': move_result['game_over'],
                'winner': move_result['winner']
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'执行AI移动时发生错误: {str(e)}',
                'original_board': board_state,
                'new_board': board_state,
                'move_executed': best_move
            }
    
    def compare_board_states(self, frontend_board: str, target_board: str) -> Dict:
        """
        对比两个棋盘状态的差异
        支持180字符格式（与spark_chess_analysis.py兼容）

        Args:
            frontend_board: 前端当前棋盘状态
            target_board: 目标棋盘状态

        Returns:
            dict: 对比结果
        """
        if not self._validate_board_state(frontend_board) or not self._validate_board_state(target_board):
            return {
                'status': 'error',
                'message': '棋盘状态格式无效',
                'is_match': False
            }

        # 直接使用180字符格式进行比较
        frontend_180 = frontend_board
        target_180 = target_board

        is_exact_match = frontend_180 == target_180

        # 计算差异位置（基于180字符格式：9列×10行）
        differences = []
        for i in range(0, 180, 2):
            pos_index = i // 2  # 位置索引（0-89）
            col = pos_index // 10  # 列（0-8）
            row = pos_index % 10   # 行（0-9）

            frontend_piece = frontend_180[i:i+2]
            target_piece = target_180[i:i+2]

            if frontend_piece != target_piece:
                differences.append({
                    'position_index': pos_index,
                    'column': col,
                    'row': row,
                    'coordinate': f"({col},{row})",
                    'frontend_piece': frontend_piece,
                    'target_piece': target_piece
                })

        return {
            'status': 'success',
            'is_match': is_exact_match,
            'difference_count': len(differences),
            'differences': differences,
            'frontend_board': frontend_180,
            'target_board': target_180
        }
    
    def get_board_analysis(self, board_state: str) -> Dict:
        """
        分析棋盘状态，获取可用的移动选项
        
        Args:
            board_state: 棋盘状态
            
        Returns:
            dict: 分析结果
        """
        if not self._validate_board_state(board_state):
            return {
                'status': 'error',
                'message': '棋盘状态格式无效'
            }
        
        if board_state not in self.board_move_map:
            return {
                'status': 'no_data',
                'message': '该棋盘状态在历史数据中未找到',
                'red_moves_count': 0,
                'black_moves_count': 0,
                'total_moves_count': 0
            }
        
        all_moves = self.board_move_map[board_state]
        red_moves = [move for move in all_moves if move['player'] == 'red']
        black_moves = [move for move in all_moves if move['player'] == 'black']
        
        return {
            'status': 'success',
            'message': '棋盘分析完成',
            'board_state': board_state,
            'red_moves_count': len(red_moves),
            'black_moves_count': len(black_moves),
            'total_moves_count': len(all_moves),
            'has_red_options': len(red_moves) > 0,
            'has_black_options': len(black_moves) > 0,
            'top_red_moves': red_moves[:3],
            'top_black_moves': black_moves[:3]
        }
    
    def _validate_board_state(self, board_state: str) -> bool:
        """验证棋盘状态格式"""
        if not board_state:
            return False
        # 只支持180字符格式
        if len(board_state) != 180:
            return False
        if not board_state.isdigit():
            return False
        return True


    
    def _validate_move_format(self, move: str) -> bool:
        """验证移动格式"""
        if not move or len(move) != 4:
            return False
        if not move.isdigit():
            return False

        try:
            from_x, from_y, to_x, to_y = int(move[0]), int(move[1]), int(move[2]), int(move[3])
            # 验证坐标范围
            if not (0 <= from_x <= 8 and 0 <= from_y <= 9):
                return False
            if not (0 <= to_x <= 8 and 0 <= to_y <= 9):
                return False
            return True
        except ValueError:
            return False

    def _validate_move_on_board(self, board_state: str, move: str, player: str) -> bool:
        """验证走法在当前棋盘状态下是否有效"""
        try:
            # 创建棋盘对象
            board = ChessBoard(board_state)

            # 解析移动坐标
            from_x = int(move[0])
            from_y = int(move[1])
            to_x = int(move[2])
            to_y = int(move[3])

            # 检查起始位置是否有棋子
            piece = board.get_piece_at(from_x, from_y)
            if not piece:
                return False

            # 检查棋子是否属于指定玩家
            if piece['type'] != player:
                return False

            # 使用规则引擎验证移动是否合法
            from .rules import ChessRules
            validation_result = ChessRules.validate_move_with_reason(board, from_x, from_y, to_x, to_y)

            return validation_result['valid']

        except Exception as e:
            print(f"验证走法时发生错误: {e}")
            return False

    def _generate_fallback_suggestions(self, board_state: str, player: str, top_k: int) -> List[Dict]:
        """当历史数据中没有匹配走法时，生成基于当前棋盘的合法走法建议"""
        try:
            # 创建棋盘对象
            board = ChessBoard(board_state)

            # 获取指定玩家的所有棋子
            player_pieces = [piece for piece in board.pieces
                           if piece['type'] == player and piece['x'] != 99 and piece['y'] != 99]

            valid_moves = []

            # 为每个棋子尝试所有可能的移动
            for piece in player_pieces:
                from_x, from_y = piece['x'], piece['y']

                # 尝试移动到棋盘上的每个位置
                for to_x in range(9):
                    for to_y in range(10):
                        if from_x == to_x and from_y == to_y:
                            continue

                        # 使用规则引擎验证移动是否合法
                        from .rules import ChessRules
                        validation_result = ChessRules.validate_move_with_reason(board, from_x, from_y, to_x, to_y)

                        if validation_result['valid']:
                            move = f"{from_x}{from_y}{to_x}{to_y}"
                            valid_moves.append({
                                'move': move,
                                'frequency': 1,  # 默认频率
                                'from_position': f"({from_x},{from_y})",
                                'to_position': f"({to_x},{to_y})",
                                'description': f"从({from_x},{from_y})移动到({to_x},{to_y})",
                                'piece_name': piece['name']
                            })

            # 返回前top_k个建议（可以根据棋子重要性或其他策略排序）
            return valid_moves[:top_k]

        except Exception as e:
            print(f"生成备用建议时发生错误: {e}")
            return []

    def _find_most_similar_board_state(self, target_board_state: str, player: str, top_k: int) -> Dict:
        """
        找到最相似的棋盘状态并返回其移动建议

        Args:
            target_board_state: 目标棋盘状态
            player: 玩家方
            top_k: 返回建议数量

        Returns:
            dict: 相似状态的建议结果
        """
        try:
            print(f"正在寻找与当前棋盘状态最相似的历史状态...")

            # 计算与所有历史棋盘状态的相似度
            similarities = []

            for board_state, moves in self.board_move_map.items():
                # 计算相似度（基于字符差异数量）
                similarity_score = self._calculate_board_similarity(target_board_state, board_state)

                # 检查该状态是否有指定玩家的移动
                player_moves = [move for move in moves if move['player'] == player]
                if player_moves:
                    similarities.append({
                        'board_state': board_state,
                        'similarity_score': similarity_score,
                        'moves': player_moves,
                        'total_moves': len(player_moves)
                    })

            if not similarities:
                return {
                    'status': 'no_similar_states',
                    'message': f'没有找到包含{player}方移动的相似棋盘状态'
                }

            # 按相似度排序（相似度越高越好）
            similarities.sort(key=lambda x: x['similarity_score'], reverse=True)

            # 选择最相似的状态
            best_match = similarities[0]
            similarity_percentage = best_match['similarity_score'] * 100

            print(f"找到最相似状态，相似度: {similarity_percentage:.1f}%")

            # 获取该状态下的移动建议
            suggestions = []
            for move_data in best_match['moves'][:top_k]:
                move = move_data['move']
                frequency = move_data['frequency']

                # 验证移动格式和在当前棋盘上的有效性
                if (self._validate_move_format(move) and
                    self._validate_move_on_board(target_board_state, move, player)):
                    suggestions.append({
                        'move': move,
                        'frequency': frequency,
                        'from_position': f"({move[0]},{move[1]})",
                        'to_position': f"({move[2]},{move[3]})",
                        'description': f"从({move[0]},{move[1]})移动到({move[2]},{move[3]})"
                    })

            # 如果相似状态的移动在当前棋盘上无效，使用备用方案
            if not suggestions:
                print("相似状态的移动在当前棋盘上无效，使用备用方案...")
                fallback_suggestions = self._generate_fallback_suggestions(target_board_state, player, top_k)
                if fallback_suggestions:
                    return {
                        'status': 'success',
                        'message': f'基于当前棋盘生成{len(fallback_suggestions)}个建议（相似状态移动无效）',
                        'board_state': target_board_state,
                        'player': player,
                        'suggestions': fallback_suggestions,
                        'similarity_mode': 'fallback',
                        'similarity_percentage': similarity_percentage
                    }
                else:
                    return {
                        'status': 'no_valid_moves',
                        'message': '无法生成有效的移动建议'
                    }

            return {
                'status': 'success',
                'message': f'基于相似棋盘状态找到{len(suggestions)}个建议（相似度{similarity_percentage:.1f}%）',
                'board_state': target_board_state,
                'player': player,
                'suggestions': suggestions,
                'similarity_mode': 'similar_state',
                'similarity_percentage': similarity_percentage,
                'similar_board_state': best_match['board_state']
            }

        except Exception as e:
            print(f"寻找相似棋盘状态时发生错误: {e}")
            return {
                'status': 'error',
                'message': f'寻找相似状态时发生错误: {str(e)}'
            }

    def _calculate_board_similarity(self, board1: str, board2: str) -> float:
        """
        计算两个棋盘状态的相似度

        Args:
            board1: 棋盘状态1
            board2: 棋盘状态2

        Returns:
            float: 相似度分数 (0.0-1.0)
        """
        if len(board1) != len(board2):
            return 0.0

        # 计算相同字符的数量
        same_chars = sum(1 for a, b in zip(board1, board2) if a == b)

        # 返回相似度百分比
        return same_chars / len(board1)
    
    def get_engine_info(self) -> Dict:
        """获取引擎信息"""
        return {
            'engine_name': 'AI Chess Suggestion Engine',
            'data_source': 'move_frequency_analysis.json',
            'total_records': len(self.frequency_data),
            'unique_board_states': len(self.board_move_map),
            'supports_red_suggestions': True,
            'supports_black_suggestions': True,
            'supports_move_execution': True,
            'supports_board_comparison': True
        }