<template>
  <div class="ai-suggestion">
    <div class="suggestion-header">
      <h3>AI建议</h3>
      <button 
        @click="getSuggestion" 
        :disabled="loading || gameOver"
        class="refresh-btn"
      >
        {{ loading ? '思考中...' : '获取建议' }}
      </button>
    </div>
    
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
    
    <div v-if="suggestion && !loading" class="suggestion-content">
      <div class="main-suggestion">
        <h4>推荐走法:</h4>
        <div class="move-text">{{ formatDetailedMove(suggestion.suggested_move || (suggestion.suggestions && suggestion.suggestions[0]?.move)) }}</div>
      </div>
    </div>
    
    <div v-if="loading" class="loading-spinner">
      <div class="spinner"></div>
      <p>AI正在分析局面...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { chessAPI } from '../services/api.js'

const props = defineProps({
  boardString: {
    type: String,
    required: true
  },
  currentPlayer: {
    type: String,
    required: true
  },
  gameOver: {
    type: Boolean,
    default: false
  },
  autoSuggest: {
    type: Boolean,
    default: true
  }
})

const suggestion = ref(null)
const loading = ref(false)
const error = ref('')

// 获取AI建议
const getSuggestion = async () => {
  if (!props.boardString || props.gameOver) return
  
  try {
    loading.value = true
    error.value = ''
    
    const response = await chessAPI.getAISuggestion(props.boardString, props.currentPlayer)
    
    if (response.status === 'success') {
      suggestion.value = response
    } else {
      error.value = response.message || 'AI建议获取失败'
    }
  } catch (err) {
    error.value = 'AI服务暂时不可用'
    console.error('获取AI建议失败:', err)
  } finally {
    loading.value = false
  }
}

// 获取棋盘上指定位置的棋子
const getPieceAt = (x, y, boardStr) => {
  if (!boardStr) return null

  // 支持180字符格式（9x10x2）
  if (boardStr.length === 180) {
    // 计算在90个位置中的索引（列行格式）
    const posIndex = x * 10 + y
    const startIndex = posIndex * 2

    if (startIndex + 1 < boardStr.length) {
      const pieceCoord = boardStr.substring(startIndex, startIndex + 2)

      // 如果该位置有棋子（不是99），则根据位置推断棋子类型
      if (pieceCoord !== "99") {
        const pieceX = parseInt(pieceCoord[0])
        const pieceY = parseInt(pieceCoord[1])

        // 验证坐标是否匹配
        if (pieceX === x && pieceY === y) {
          return identifyPieceAtPosition(x, y)
        }
      }
    }
    return null
  }

  // 兼容64字符格式
  const redNames = ['车', '马', '相', '仕', '帅', '仕', '相', '马', '车', '炮', '炮', '兵', '兵', '兵', '兵', '兵']
  const blackNames = ['车', '马', '象', '士', '将', '士', '象', '马', '车', '炮', '炮', '卒', '卒', '卒', '卒', '卒']

  // 检查红方棋子
  for (let i = 0; i < 16; i++) {
    const pieceX = parseInt(boardStr[i * 2])
    const pieceY = parseInt(boardStr[i * 2 + 1])
    if (pieceX === x && pieceY === y && pieceX !== 9 && pieceY !== 9) {
      return { name: redNames[i], type: 'red' }
    }
  }

  // 检查黑方棋子
  for (let i = 0; i < 16; i++) {
    const pieceX = parseInt(boardStr[32 + i * 2])
    const pieceY = parseInt(boardStr[32 + i * 2 + 1])
    if (pieceX === x && pieceY === y && pieceX !== 9 && pieceY !== 9) {
      return { name: blackNames[i], type: 'black' }
    }
  }

  return null
}

// 根据位置识别棋子类型（基于标准中国象棋初始布局）
const identifyPieceAtPosition = (x, y) => {
  // 黑方棋子（上方，y=0-4）
  if (y === 0) {  // 第0行：黑方后排
    const pieces = ['车', '马', '象', '士', '将', '士', '象', '马', '车']
    if (x >= 0 && x < pieces.length) {
      return { name: pieces[x], type: 'black' }
    }
  } else if (y === 2) {  // 第2行：黑方炮
    if (x === 1 || x === 7) {
      return { name: '炮', type: 'black' }
    }
  } else if (y === 3) {  // 第3行：黑方兵
    if ([0, 2, 4, 6, 8].includes(x)) {
      return { name: '卒', type: 'black' }
    }
  }

  // 红方棋子（下方，y=5-9）
  else if (y === 6) {  // 第6行：红方兵
    if ([0, 2, 4, 6, 8].includes(x)) {
      return { name: '兵', type: 'red' }
    }
  } else if (y === 7) {  // 第7行：红方炮
    if (x === 1 || x === 7) {
      return { name: '炮', type: 'red' }
    }
  } else if (y === 9) {  // 第9行：红方后排
    const pieces = ['车', '马', '相', '仕', '帅', '仕', '相', '马', '车']
    if (x >= 0 && x < pieces.length) {
      return { name: pieces[x], type: 'red' }
    }
  }

  return null
}

// 格式化详细走法显示
const formatDetailedMove = (move) => {
  if (!move || move.length !== 4) return '暂无建议'
  
  const fromX = parseInt(move[0])
  const fromY = parseInt(move[1])
  const toX = parseInt(move[2])
  const toY = parseInt(move[3])
  
  const piece = getPieceAt(fromX, fromY, props.boardString)
  if (!piece) return '无效走法'
  
  // 计算移动方向和距离
  const isRed = piece.type === 'red'

  // 根据棋子颜色确定进退方向
  let direction
  if (toY === fromY) {
    direction = '平'
  } else if (isRed ? toY < fromY : toY > fromY) {
    direction = '进'
  } else {
    direction = '退'
  }

  // 步数或目标列
  const steps = direction === '平'
    ? (isRed ? toX + 1 : 9 - toX)
    : Math.abs(toY - fromY)

  // 棋子起始列描述 (从己方视角1-9)
  const position = isRed ? fromX + 1 : 9 - fromX

  return `${piece.name}${position}${direction}${steps}`
}

// 获取最高概率
const getTopMoveConfidence = () => {
  if (!suggestion.value?.suggestions || suggestion.value.suggestions.length === 0) return null
  
  const topMove = suggestion.value.suggestions[0]
  return topMove?.confidence ? Math.round(topMove.confidence * 100) : null
}

// 监听棋盘变化，自动获取建议
watch(() => [props.boardString, props.currentPlayer], () => {
  if (props.autoSuggest && props.currentPlayer === 'red' && !props.gameOver) {
    setTimeout(() => {
      getSuggestion()
    }, 500) // 延迟500ms避免频繁请求
  }
}, { deep: true })
</script>

<style scoped>
.ai-suggestion {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  min-width: 280px;
  width: 320px;
  height: fit-content;
}

.suggestion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.suggestion-header h3 {
  margin: 0;
  color: #495057;
  font-size: 18px;
}

.refresh-btn {
  padding: 8px 16px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.refresh-btn:hover:not(:disabled) {
  background: #0056b3;
}

.refresh-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.error-message {
  color: #dc3545;
  padding: 8px;
  background: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
  margin-bottom: 16px;
}

.suggestion-content {
  space-y: 16px;
}

.main-suggestion {
  background: #e7f3ff;
  padding: 12px;
  border-radius: 6px;
  border-left: 4px solid #007bff;
  margin-bottom: 16px;
}

.main-suggestion h4 {
  margin: 0 0 8px 0;
  color: #495057;
  font-size: 14px;
  font-weight: 600;
}

.move-text {
  font-size: 18px;
  font-weight: bold;
  color: #007bff;
}

.confidence-text {
  margin-top: 8px;
  font-size: 14px;
  color: #6c757d;
  font-weight: 500;
}

.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-spinner p {
  color: #6c757d;
  margin: 0;
  font-size: 14px;
}
</style>