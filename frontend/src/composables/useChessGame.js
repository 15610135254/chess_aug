import { ref, reactive, computed } from 'vue'
import { chessAPI } from '../services/api.js'

export function useChessGame() {
  const boardString = ref('')
  const currentPlayer = ref('red')
  const selectedPiece = ref(null)
  const gameOver = ref(false)
  const winner = ref('')
  const loading = ref(false)
  const error = ref('')
  const aiThinking = ref(false)
  const gameMode = ref('human_vs_ai') // 人机对战模式

  // 棋子初始数据
  const pieces = reactive([])

  // 棋盘网格大小
  const BOARD_WIDTH = 9
  const BOARD_HEIGHT = 10
  const CELL_SIZE = 50

  // 初始化游戏
  const initGame = async () => {
    try {
      loading.value = true
      error.value = ''
      
      const response = await chessAPI.initBoard()
      if (response.status === 'success') {
        boardString.value = response.board
        parseBoardString(response.board)
        currentPlayer.value = 'red'
        selectedPiece.value = null
        gameOver.value = false
        winner.value = ''
        
        console.log('游戏初始化完成，当前玩家:', currentPlayer.value)
      } else {
        error.value = response.message || '初始化失败'
      }
    } catch (err) {
      error.value = '连接服务器失败'
      console.error('初始化游戏失败:', err)
    } finally {
      loading.value = false
    }
  }

  // 解析棋盘字符串（180字符格式：9列×10行×2字符每位置）
  const parseBoardString = (boardStr) => {
    pieces.length = 0

    // 验证棋盘字符串长度
    if (boardStr.length !== 180) {
      console.error('棋盘字符串长度错误，期望180字符，实际:', boardStr.length)
      return
    }

    // 棋子名称映射（根据位置确定棋子类型）
    const getPieceName = (x, y, isRed) => {
      if (isRed) {
        // 红方棋子
        if (y === 9) {
          // 第9行：车马相仕帅仕相马车
          const names = ['车', '马', '相', '仕', '帅', '仕', '相', '马', '车']
          return names[x] || '未知'
        } else if (y === 7) {
          // 第7行：炮
          return '炮'
        } else if (y === 6) {
          // 第6行：兵
          return '兵'
        }
      } else {
        // 黑方棋子
        if (y === 0) {
          // 第0行：车马象士将士象马车
          const names = ['车', '马', '象', '士', '将', '士', '象', '马', '车']
          return names[x] || '未知'
        } else if (y === 2) {
          // 第2行：炮
          return '炮'
        } else if (y === 3) {
          // 第3行：卒
          return '卒'
        }
      }
      return '未知'
    }

    // 解析180字符格式：每2个字符表示一个位置的坐标
    for (let i = 0; i < 180; i += 2) {
      const posStr = boardStr.substr(i, 2)

      // 跳过空位置（99表示空）
      if (posStr === '99') continue

      // 解析坐标
      const x = parseInt(posStr[0])
      const y = parseInt(posStr[1])

      // 验证坐标有效性
      if (isNaN(x) || isNaN(y) || x < 0 || x > 8 || y < 0 || y > 9) {
        continue
      }

      // 根据位置判断是红方还是黑方棋子
      const isRed = y >= 6 // 第6行及以下是红方
      const pieceName = getPieceName(x, y, isRed)

      // 生成唯一ID
      const pieceId = `${isRed ? 'red' : 'black'}_${x}_${y}`

      pieces.push({
        id: pieceId,
        name: pieceName,
        x: x,
        y: y,
        type: isRed ? 'red' : 'black',
        color: isRed ? '#d32f2f' : '#1976d2',
        bgcolor: isRed ? '#ffebee' : '#e3f2fd',
        bgColor_b: isRed ? '#d32f2f' : '#1976d2'
      })
    }

    console.log('解析完成，棋子数量:', pieces.length)
    console.log('棋子列表:', pieces)
  }

  // 获取指定位置的棋子
  const getPieceAt = (x, y) => {
    return pieces.find(piece => piece.x === x && piece.y === y)
  }

  // 选择棋子
  const selectPiece = (x, y) => {
    const piece = getPieceAt(x, y)
    
    if (piece && piece.type === currentPlayer.value) {
      selectedPiece.value = { x, y, piece }
      return true
    }
    return false
  }

  // 移动棋子
  const movePiece = async (toX, toY) => {
    if (!selectedPiece.value) return false

    const fromX = selectedPiece.value.x
    const fromY = selectedPiece.value.y
    const moveString = `${fromX}${fromY}${toX}${toY}`

    try {
      loading.value = true
      error.value = ''

      const response = await chessAPI.movePiece(boardString.value, moveString)
      
      if (response.status === 'success') {
        console.log('DEBUG movePiece: 移动成功，更新棋盘状态')
        console.log('DEBUG movePiece: 移动前棋盘状态:', boardString.value)
        console.log('DEBUG movePiece: 移动后棋盘状态:', response.board)
        console.log('DEBUG movePiece: 移动前棋子数量:', pieces.length)

        boardString.value = response.board
        parseBoardString(response.board)

        console.log('DEBUG movePiece: 解析后棋子数量:', pieces.length)

        // 检查游戏是否结束
        if (response.game_over) {
          gameOver.value = true
          winner.value = response.winner
          selectedPiece.value = null

          // 显示胜利消息
          const winnerName = response.winner === 'red' ? '红方' : '黑方'
          error.value = `游戏结束！${winnerName}获胜！`
        } else {
          // 切换玩家
          currentPlayer.value = currentPlayer.value === 'red' ? 'black' : 'red'
          selectedPiece.value = null

          // 如果切换到黑方且为人机对战模式，触发AI走法
          console.log('回合切换到:', currentPlayer.value, '游戏模式:', gameMode.value)
          if (currentPlayer.value === 'black' && gameMode.value === 'human_vs_ai') {
            console.log('触发AI走法')
            setTimeout(() => {
              makeAIMove()
            }, 1000) // 延迟1秒让用户看到棋子移动
          }
        }

        return true
      } else if (response.status === 'invalid') {
        console.error('移动被拒绝:', response.message)
        error.value = '无效移动: ' + (response.message || '')
        return false
      } else {
        console.error('移动失败:', response)
        error.value = response.message || '移动失败'
        return false
      }
    } catch (err) {
      error.value = '移动失败'
      console.error('移动棋子失败:', err)
      return false
    } finally {
      loading.value = false
    }
  }

  // AI自动走法
  const makeAIMove = async () => {
    if (gameOver.value || loading.value || aiThinking.value) {
      console.log('AI走法被阻止:', { gameOver: gameOver.value, loading: loading.value, aiThinking: aiThinking.value })
      return
    }
    if (currentPlayer.value !== 'black') {
      console.log('不是黑方回合，当前玩家:', currentPlayer.value)
      return
    }

    console.log('开始AI走法，当前棋盘:', boardString.value)
    console.log('DEBUG makeAIMove: 当前棋子数量:', pieces.length)

    try {
      aiThinking.value = true
      error.value = ''

      // 直接调用AI执行移动接口
      console.log('调用AI执行移动接口...')
      const response = await chessAPI.blackAutoMove(boardString.value)
      console.log('AI移动响应:', response)

      if (response.status === 'success') {
        console.log('DEBUG makeAIMove: AI移动成功')
        console.log('DEBUG makeAIMove: 移动前棋盘:', response.original_board)
        console.log('DEBUG makeAIMove: 移动后棋盘:', response.new_board)
        console.log('DEBUG makeAIMove: 执行的移动:', response.move_executed)

        // 更新棋盘状态
        boardString.value = response.new_board
        parseBoardString(response.new_board)

        console.log('DEBUG makeAIMove: 更新后棋子数量:', pieces.length)

        // 检查游戏是否结束
        if (response.game_over) {
          gameOver.value = true
          winner.value = response.winner
          selectedPiece.value = null

          const winnerName = response.winner === 'red' ? '红方' : '黑方'
          error.value = `游戏结束！${winnerName}获胜！`
        } else {
          // 切换回红方
          currentPlayer.value = 'red'
          selectedPiece.value = null
        }
      } else {
        console.error('AI移动失败:', response)
        error.value = response.message || 'AI移动失败'
      }
    } catch (err) {
      console.error('AI走法异常:', err)
      error.value = 'AI走法失败: ' + err.message
    } finally {
      aiThinking.value = false
      console.log('AI走法结束')
    }
  }

  // 处理棋盘点击
  const handleBoardClick = async (x, y) => {
    if (gameOver.value || loading.value || aiThinking.value) return
    
    // 人机对战模式下，只允许红方操作
    if (gameMode.value === 'human_vs_ai' && currentPlayer.value === 'black') {
      return
    }

    if (selectedPiece.value) {
      // 已选中棋子，尝试移动
      const success = await movePiece(x, y)
      if (!success) {
        // 移动失败，尝试选择新棋子
        if (!selectPiece(x, y)) {
          selectedPiece.value = null
        }
      }
    } else {
      // 未选中棋子，尝试选择
      selectPiece(x, y)
    }
  }

  // 重新开始游戏
  const restartGame = () => {
    initGame()
  }

  // 计算属性
  const isSelected = computed(() => (x, y) => {
    return selectedPiece.value && 
           selectedPiece.value.x === x && 
           selectedPiece.value.y === y
  })

  const canMove = computed(() => {
    if (gameOver.value || loading.value || aiThinking.value) return false
    // 人机对战模式下，黑方不能手动操作
    if (gameMode.value === 'human_vs_ai' && currentPlayer.value === 'black') return false
    return true
  })
  
  const isAITurn = computed(() => {
    return gameMode.value === 'human_vs_ai' && currentPlayer.value === 'black'
  })

  return {
    // 状态
    pieces,
    currentPlayer,
    selectedPiece,
    gameOver,
    winner,
    loading,
    error,
    boardString,
    aiThinking,
    gameMode,

    // 常量
    BOARD_WIDTH,
    BOARD_HEIGHT,
    CELL_SIZE,

    // 方法
    initGame,
    handleBoardClick,
    restartGame,
    getPieceAt,
    makeAIMove,

    // 计算属性
    isSelected,
    canMove,
    isAITurn
  }
}
