const API_BASE = "http://localhost:8080";

// Tailwind utility classes
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".input").forEach(el => {
    el.classList.add(
      "w-full",
      "border",
      "rounded",
      "px-3",
      "py-2",
      "mb-2",
      "focus:outline-none",
      "focus:ring"
    );
  });

  document.querySelectorAll(".btn").forEach(el => {
    el.classList.add(
      "bg-blue-600",
      "text-white",
      "px-4",
      "py-2",
      "rounded",
      "hover:bg-blue-700"
    );
  });
});

function setToken(token) {
  localStorage.setItem("token", token);
}

function getToken() {
  return localStorage.getItem("token");
}

async function register() {
  await fetch(`${API_BASE}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      username: document.getElementById("reg-username").value,
      password: document.getElementById("reg-password").value
    })
  });
  alert("Registered. You can login now.");
}

async function login() {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      username: document.getElementById("login-username").value,
      password: document.getElementById("login-password").value
    })
  });
  const data = await res.json();
  setToken(data.token);
  window.location = "posts.html";
}

async function loadPosts() {
  const res = await fetch(`${API_BASE}/posts`);
  const posts = await res.json();
  const ul = document.getElementById("post-list");
  ul.innerHTML = "";
  posts.forEach(p => {
    const li = document.createElement("li");
    li.innerHTML = `<a href="post.html?id=${p.id}">${p.title}</a>`;
    ul.appendChild(li);
  });
}

async function createPost() {
  await fetch(`${API_BASE}/posts`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${getToken()}`
    },
    body: JSON.stringify({
      title: document.getElementById("post-title").value,
      content: document.getElementById("post-content").value
    })
  });
  loadPosts();
}

function getPostId() {
  return new URLSearchParams(window.location.search).get("id");
}

async function loadPost() {
  const id = getPostId();
  const res = await fetch(`${API_BASE}/posts/${id}`);
  const post = await res.json();
  document.getElementById("post-title").innerText = post.title;
  document.getElementById("post-content").innerText = post.content;
  const ul = document.getElementById("comment-list");
  ul.innerHTML = "";
  post.comments.forEach(c => {
    const li = document.createElement("li");
    li.innerText = c.content;
    ul.appendChild(li);
  });
}

async function addComment() {
  const id = getPostId();
  await fetch(`${API_BASE}/posts/${id}/comments`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${getToken()}`
    },
    body: JSON.stringify({
      content: document.getElementById("comment-content").value
    })
  });
  loadPost();
}
