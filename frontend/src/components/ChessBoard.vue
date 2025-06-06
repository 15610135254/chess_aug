<template>
  <div class="chess-board-container">
    <canvas 
      ref="canvasRef"
      :width="canvasWidth"
      :height="canvasHeight"
      @click="handleCanvasClick"
      class="chess-board"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'

const props = defineProps({
  pieces: {
    type: Array,
    default: () => []
  },
  selectedPiece: {
    type: Object,
    default: null
  },
  boardWidth: {
    type: Number,
    default: 9
  },
  boardHeight: {
    type: Number,
    default: 10
  },
  cellSize: {
    type: Number,
    default: 50
  }
})

const emit = defineEmits(['board-click'])

const canvasRef = ref(null)

// 计算画布尺寸，确保棋盘居中显示
const boardActualWidth = (props.boardWidth - 1) * props.cellSize
const boardActualHeight = (props.boardHeight - 1) * props.cellSize
const margin = 80 // 棋盘四周的边距
const canvasWidth = ref(boardActualWidth + margin * 2)
const canvasHeight = ref(boardActualHeight + margin * 2)

// 计算偏移量，让棋盘在画布中居中
const getOffsets = () => {
  const offsetX = (canvasWidth.value - boardActualWidth) / 2
  const offsetY = (canvasHeight.value - boardActualHeight) / 2
  return { offsetX, offsetY }
}

// 绘制棋盘
const drawBoard = () => {
  const canvas = canvasRef.value
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  const { cellSize, boardWidth, boardHeight } = props

  // 清空画布
  ctx.clearRect(0, 0, canvas.width, canvas.height)

  // 获取动态计算的偏移量，让棋盘居中
  const { offsetX, offsetY } = getOffsets()
  
  // 绘制背景
  ctx.fillStyle = '#f5f5dc'
  ctx.fillRect(offsetX - 25, offsetY - 25, boardActualWidth + 50, boardActualHeight + 50)
  
  // 绘制网格线
  ctx.strokeStyle = '#8b4513'
  ctx.lineWidth = 2
  
  // 垂直线
  for (let i = 0; i <= boardWidth - 1; i++) {
    const x = offsetX + i * cellSize

    // 最左边和最右边的垂直线保持完整
    if (i === 0 || i === boardWidth - 1) {
      ctx.beginPath()
      ctx.moveTo(x, offsetY)
      ctx.lineTo(x, offsetY + (boardHeight - 1) * cellSize)
      ctx.stroke()
    } else {
      // 中间的垂直线在楚河汉界区域完全断开
      const riverTopY = offsetY + 4 * cellSize
      const riverBottomY = offsetY + 5 * cellSize

      // 绘制上半段垂直线（从顶部到第4行）
      ctx.beginPath()
      ctx.moveTo(x, offsetY)
      ctx.lineTo(x, riverTopY)
      ctx.stroke()

      // 绘制下半段垂直线（从第5行到底部）
      ctx.beginPath()
      ctx.moveTo(x, riverBottomY)
      ctx.lineTo(x, offsetY + (boardHeight - 1) * cellSize)
      ctx.stroke()
    }
  }
  
  // 水平线
  for (let i = 0; i <= boardHeight - 1; i++) {
    ctx.beginPath()
    ctx.moveTo(offsetX, offsetY + i * cellSize)
    ctx.lineTo(offsetX + (boardWidth - 1) * cellSize, offsetY + i * cellSize)
    ctx.stroke()
  }
  
  // 绘制楚河汉界
  ctx.font = '16px Arial'
  ctx.fillStyle = '#8b4513'
  ctx.textAlign = 'center'
  ctx.fillText('楚河', offsetX + cellSize * 2, offsetY + cellSize * 4.5 + 5)
  ctx.fillText('汉界', offsetX + cellSize * 6, offsetY + cellSize * 4.5 + 5)
  
  // 绘制九宫格斜线
  // 红方九宫格
  ctx.beginPath()
  ctx.moveTo(offsetX + 3 * cellSize, offsetY + 7 * cellSize)
  ctx.lineTo(offsetX + 5 * cellSize, offsetY + 9 * cellSize)
  ctx.stroke()

  ctx.beginPath()
  ctx.moveTo(offsetX + 5 * cellSize, offsetY + 7 * cellSize)
  ctx.lineTo(offsetX + 3 * cellSize, offsetY + 9 * cellSize)
  ctx.stroke()

  // 黑方九宫格
  ctx.beginPath()
  ctx.moveTo(offsetX + 3 * cellSize, offsetY)
  ctx.lineTo(offsetX + 5 * cellSize, offsetY + 2 * cellSize)
  ctx.stroke()

  ctx.beginPath()
  ctx.moveTo(offsetX + 5 * cellSize, offsetY)
  ctx.lineTo(offsetX + 3 * cellSize, offsetY + 2 * cellSize)
  ctx.stroke()
}

// 绘制棋子
const drawPieces = () => {
  const canvas = canvasRef.value
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  const { cellSize } = props
  const { offsetX, offsetY } = getOffsets()
  const pieceRadius = cellSize * 0.4

  props.pieces.forEach(piece => {
    const x = offsetX + piece.x * cellSize
    const y = offsetY + piece.y * cellSize

    // 绘制选中状态的高亮
    if (props.selectedPiece &&
        props.selectedPiece.x === piece.x &&
        props.selectedPiece.y === piece.y) {
      ctx.fillStyle = '#ffeb3b'
      ctx.beginPath()
      ctx.arc(x, y, pieceRadius + 5, 0, 2 * Math.PI)
      ctx.fill()
    }

    // 绘制棋子背景圆
    ctx.fillStyle = piece.bgcolor
    ctx.beginPath()
    ctx.arc(x, y, pieceRadius, 0, 2 * Math.PI)
    ctx.fill()

    // 绘制棋子边框
    ctx.strokeStyle = piece.bgColor_b
    ctx.lineWidth = 2
    ctx.beginPath()
    ctx.arc(x, y, pieceRadius, 0, 2 * Math.PI)
    ctx.stroke()

    // 绘制棋子文字
    ctx.fillStyle = piece.color
    ctx.font = `${cellSize * 0.6}px Arial`
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(piece.name, x, y)
  })
}

// 处理画布点击
const handleCanvasClick = (event) => {
  const canvas = canvasRef.value
  if (!canvas) return

  const rect = canvas.getBoundingClientRect()
  const clickX = event.clientX - rect.left
  const clickY = event.clientY - rect.top

  const { offsetX, offsetY } = getOffsets()
  const { cellSize } = props

  // 计算点击的网格坐标
  const gridX = Math.round((clickX - offsetX) / cellSize)
  const gridY = Math.round((clickY - offsetY) / cellSize)

  // 检查坐标是否在棋盘范围内
  if (gridX >= 0 && gridX < props.boardWidth &&
      gridY >= 0 && gridY < props.boardHeight) {
    emit('board-click', gridX, gridY)
  }
}

// 重绘整个棋盘
const redraw = () => {
  nextTick(() => {
    drawBoard()
    drawPieces()
  })
}

// 监听棋子变化
watch(() => props.pieces, redraw, { deep: true })
watch(() => props.selectedPiece, redraw, { deep: true })

// 组件挂载后初始化
onMounted(() => {
  redraw()
})
</script>

<style scoped>
.chess-board-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 0;
}

.chess-board {
  border: 2px solid #8b4513;
  border-radius: 8px;
  cursor: pointer;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.chess-board:hover {
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
}
</style>
