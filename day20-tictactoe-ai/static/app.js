/*
  Simple Tic Tac Toe (Player X vs Computer O) with Chat Assistant and WebSocket Tool Calling
  - Player clicks a cell to place 'X'
  - App calls /api/next_move with current board to get computer 'O' move
  - Detect wins/draws and allow reset
  - Chat with assistant using /api/complete endpoint with streaming
  - WebSocket connection for receiving tool calls from assistant
*/

const SIZE = 3;
const CELLS = SIZE * SIZE; // 9

// Generate a random client ID for this session
const CLIENT_ID = 'client_' + Math.random().toString(36).substr(2, 9);

// WebSocket connection
let websocket = null;

// Chat state
let chatHistory = [
  { role: "assistant", content: "Hi! I'm here to help you with tic tac toe. I can even make moves for you if you ask! Ask me anything about strategy or just chat!" }
];

function createBoardElement(onCellClick) {
  const boardEl = document.getElementById('board');
  boardEl.innerHTML = '';
  for (let i = 0; i < CELLS; i++) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'cell';
    btn.setAttribute('data-idx', String(i));
    btn.setAttribute('aria-label', `Cell ${i + 1}`);
    btn.addEventListener('click', () => onCellClick(i));
    boardEl.appendChild(btn);
  }
  return boardEl;
}

function checkWinner(board) {
  const lines = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6],
  ];
  for (const [a, b, c] of lines) {
    if (board[a] && board[a] === board[b] && board[a] === board[c]) {
      return board[a]; // 'X' or 'O'
    }
  }
  if (board.every((v) => v)) return 'Draw';
  return null; // no winner yet
}



function render(board) {
  const boardEl = document.getElementById('board');
  for (let i = 0; i < CELLS; i++) {
    const btn = boardEl.children[i];
    btn.textContent = board[i] || '';
    btn.disabled = Boolean(board[i]);
  }
}

function setStatus(text, isError = false) {
  const el = document.getElementById('status');
  el.textContent = text;
  el.classList.toggle('error', isError);
}

async function getComputerMove(board) {
  const payload = { board: board.map((v) => (v ? v : null)) };
  const res = await fetch('/api/next_move', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  if (typeof data.index !== 'number') throw new Error('Invalid response');
  return data.index;
}

// Chat functions
function addMessageToChat(role, content, isStreaming = false, isSystemMessage = false) {
  const messagesContainer = document.getElementById('chat-messages');
  const messageDiv = document.createElement('div');
  messageDiv.className = `message ${role}${isStreaming ? ' streaming' : ''}${isSystemMessage ? ' system' : ''}`;
  
  const contentDiv = document.createElement('div');
  contentDiv.className = 'message-content';
  contentDiv.textContent = content;
  
  messageDiv.appendChild(contentDiv);
  messagesContainer.appendChild(messageDiv);
  
  // Scroll to bottom
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
  
  return messageDiv;
}

function getBoardStatusMessage(board) {
  const boardStr = board.map((cell, idx) => {
    const row = Math.floor(idx / 3);
    const col = idx % 3;
    return cell ? `(${row},${col}):${cell}` : `(${row},${col}):empty`;
  }).join(' ');
  
  return `Current board state: ${boardStr}. Note: positions are (row,column) where both start from 0.`;
}

function getCurrentGameStatus(board, gameState) {
  const winner = checkWinner(board);
  if (winner) {
    return winner === 'Draw' ? 'Game ended in a draw.' : `Game over, ${winner} won.`;
  }
  
  if (gameState.playerTurn) {
    return 'It\'s the player\'s turn (X).';
  } else {
    return 'It\'s the computer\'s turn (O).';
  }
}

function updateMessageContent(messageElement, content) {
  const contentDiv = messageElement.querySelector('.message-content');
  contentDiv.textContent = content;
  
  // Scroll to bottom
  const messagesContainer = document.getElementById('chat-messages');
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

async function sendChatMessage(userMessage, gameBoard = null, gameState = null) {
  // Add user message to UI and history
  addMessageToChat('user', userMessage);
  chatHistory.push({ role: "user", content: userMessage });
  
  // If board state is provided, add it as a system message
  if (gameBoard && gameState) {
    const boardMessage = getBoardStatusMessage(gameBoard);
    const statusMessage = getCurrentGameStatus(gameBoard, gameState);
    const systemMessage = `${boardMessage} ${statusMessage}`;
    
    // Add to chat history but not to UI (system message)
    chatHistory.push({ role: "user", content: systemMessage });
  }
  
  // Create assistant message element for streaming
  const assistantMessageEl = addMessageToChat('assistant', '', true);
  let assistantResponse = '';
  
  try {
    const response = await fetch(`/api/complete?client_id=${CLIENT_ID}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({payload: chatHistory}),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No response body');
    }
    
    const decoder = new TextDecoder();
    
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data === '[DONE]') {
            // End of stream
            assistantMessageEl.classList.remove('streaming');
            chatHistory.push({ role: "assistant", content: assistantResponse });
            return;
          }
          if (data.trim()) {
            assistantResponse += data;
            updateMessageContent(assistantMessageEl, assistantResponse);
          }
        }
      }
    }
    
    // Fallback in case [DONE] wasn't received
    assistantMessageEl.classList.remove('streaming');
    if (assistantResponse) {
      chatHistory.push({ role: "assistant", content: assistantResponse });
    }
    
  } catch (error) {
    console.error('Chat error:', error);
    updateMessageContent(assistantMessageEl, 'Sorry, I encountered an error. Please try again.');
    assistantMessageEl.classList.remove('streaming');
    assistantMessageEl.classList.add('error');
  }
}

function setupChat() {
  const chatInput = document.getElementById('chat-input');
  const sendBtn = document.getElementById('send-btn');
  
  async function handleSend() {
    const message = chatInput.value.trim();
    if (!message) return;
    
    chatInput.value = '';
    sendBtn.disabled = true;
    chatInput.disabled = true;
    
    // Get current game state to pass to chat
    const currentBoard = window.gameState ? window.gameState.board : null;
    const currentState = window.gameState;
    
    await sendChatMessage(message, currentBoard, currentState);
    
    sendBtn.disabled = false;
    chatInput.disabled = false;
    chatInput.focus();
  }
  
  sendBtn.addEventListener('click', handleSend);
  
  chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  });
}

function newGame() {
  const state = {
    board: Array(CELLS).fill(null), // values: 'X' | 'O' | null
    playerTurn: true,
    over: false,
  };
  return state;
}

window.addEventListener('DOMContentLoaded', () => {
  const state = newGame();
  // Make state available globally for chat
  window.gameState = state;
  
// WebSocket functions
function initWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws/${CLIENT_ID}`;
  
  websocket = new WebSocket(wsUrl);
  
  websocket.onopen = function(event) {
    console.log('WebSocket connected with client ID:', CLIENT_ID);
    setStatus('Connected to game assistant');
  };
  
  websocket.onmessage = function(event) {
    try {
      const message = JSON.parse(event.data);
      handleWebSocketMessage(message);
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  };
  
  websocket.onerror = function(error) {
    console.error('WebSocket error:', error);
    setStatus('Connection error', true);
  };
  
  websocket.onclose = function(event) {
    console.log('WebSocket connection closed');
    setStatus('Disconnected from assistant', true);
    // Attempt to reconnect after 3 seconds
    setTimeout(initWebSocket, 3000);
  };
}

function handleWebSocketMessage(message) {
  console.log('Received WebSocket message:', message);
  
  if (message.action === 'play') {
    const { row, column } = message.payload;
    makeAssistantMove(row, column);
  } else if (message.type === 'echo') {
    console.log('Echo from server:', message.data);
  }
}

function makeAssistantMove(row, column) {
  onPlayerClick(row * 3 + column)
  setStatus('Your turn (X)');
}

  // Initialize WebSocket connection
  initWebSocket();
  
  createBoardElement(onPlayerClick);
  render(state.board);
  setupChat();
  
  document.getElementById('reset').addEventListener('click', () => {
    const fresh = newGame();
    Object.assign(state, fresh);
    window.gameState = state; // Update global reference
    render(state.board);
    setStatus('Your turn (X)');
  });

  async function onPlayerClick(i) {
    if (state.over || !state.playerTurn || state.board[i]) return;
    // Player move
    state.board[i] = 'X';
    render(state.board);

    // Check player result
    let result = checkWinner(state.board);
    if (result) {
      state.over = true;
      setStatus(result === 'Draw' ? 'Draw!' : 'You win!');
      return;
    }

    // Computer move (only if assistant isn't controlling the game)
    state.playerTurn = false;
    setStatus('Computer thinking…');
    try {
      const idx = await getComputerMove(state.board);
      if (!state.board[idx]) {
        state.board[idx] = 'O';
      }
    } catch (err) {
      setStatus(`Error: ${err.message}`, true);
      state.playerTurn = true;
      return;
    }

    render(state.board);
    result = checkWinner(state.board);
    if (result) {
      state.over = true;
      setStatus(result === 'Draw' ? 'Draw!' : 'Computer wins!');
      return;
    }

    state.playerTurn = true;
    setStatus('Your turn (X)');
  }
});

