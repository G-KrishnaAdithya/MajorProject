const BASE_URL = 'http://localhost:8002'; // Update if backend runs on different port

// Show username on home page
window.onload = function () {
  const usernameDisplay = document.getElementById('username-display');
  if (usernameDisplay) {
    const username = localStorage.getItem('username');
    if (!username) {
      window.location.href = 'login.html'; // Redirect if not logged in
    } else {
      usernameDisplay.textContent = username;
    }
  }
};

// LOGIN
function login() {
  const username = document.getElementById('login-username').value;
  const password = document.getElementById('login-password').value;

  fetch(`${BASE_URL}/user/login`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ username, password })
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        localStorage.setItem('username', username);
        window.location.href = 'index.html';
      } else {
        alert(data.errors[0].message);
      }
    });
}

// SIGNUP
function signup() {
  const username = document.getElementById('signup-username').value;
  const password = document.getElementById('signup-password').value;
  const email = document.getElementById('signup-email').value;
  const phone = document.getElementById('signup-phone').value;
  const ad_agency_name = document.getElementById('signup-agency').value;

  const payload = {
    username,
    password,
    email: email || undefined,
    phone: phone || undefined,
    ad_agency_name: ad_agency_name || undefined
  };

  fetch(`${BASE_URL}/user/signup`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(payload)
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        alert('Signup successful! Please login.');
        window.location.href = 'login.html';
      } else {
        alert(data.errors[0].message);
      }
    });
}

// GENERATE VIDEO
function generateVideo() {
  const story = document.getElementById('story').value;
  const username = localStorage.getItem('username');

  if (!story) {
    alert('Please enter a story!');
    return;
  }

  fetch(`${BASE_URL}/storyboard/generate`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ username, story })
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        alert('Video generated!');
        fetchVideos();
      } else {
        alert('Error generating video');
      }
    });
}

// FETCH PREVIOUS VIDEOS
function fetchVideos() {
  const username = localStorage.getItem('username');

  fetch(`${BASE_URL}/storyboard/get_storyboards?username=${username}`)
    .then(res => res.json())
    .then(data => {
      const list = document.getElementById('video-list');
      list.innerHTML = '';

      if (data.success && data.data.length > 0) {
        data.data.forEach(entry => {
          const item = document.createElement('div');
          item.innerHTML = `
            <p><strong>Story:</strong> ${entry.story}</p>
            <video src="${entry.video}" controls width="100%"></video>
            alert('Video generated!');
            
            <hr/>
          `;
          list.appendChild(item);
        });
      } else {
        list.innerHTML = '<p>No videos found.</p>';
      }
    });
}

// LOGOUT
function logout() {
  localStorage.removeItem('username');
  window.location.href = 'login.html';
}
