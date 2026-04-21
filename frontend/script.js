const API = "http://18.130.226.110:8000";

// ----- UTILITIES -----
function showMessage(id, text, type) {
    const el = document.getElementById(id);
    el.textContent = text;
    el.className = `message ${type}`;
}

function getToken() {
    return localStorage.getItem("token");
}

function getAccount() {
    return localStorage.getItem("account_number");
}

// ----- REGISTER -----
async function register() {
    const username = document.getElementById("username").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    if (!username || !email || !password) {
        showMessage("msg", "Please fill in all fields", "error");
        return;
    }

    const btn = document.getElementById("register-btn");
    btn.disabled = true;
    btn.textContent = "Registering...";

    try {
        const res = await fetch(`${API}/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, email, password })
        });
        const data = await res.json();

        if (data.account_number) {
            showMessage("msg", `Account created! Your account number: ${data.account_number}`, "success");
            setTimeout(() => window.location.href = "index.html", 3000);
        } else {
            showMessage("msg", data.detail || "Registration failed", "error");
        }
    } catch (err) {
        showMessage("msg", "Server error — is backend running?", "error");
    }

    btn.disabled = false;
    btn.textContent = "Register";
}

// ----- LOGIN -----
async function login() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    if (!username || !password) {
        showMessage("msg", "Please fill in all fields", "error");
        return;
    }

    const btn = document.getElementById("login-btn");
    btn.disabled = true;
    btn.textContent = "Logging in...";

    try {
        const form = new URLSearchParams();
        form.append("username", username);
        form.append("password", password);

        const res = await fetch(`${API}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: form
        });
        const data = await res.json();

        if (data.access_token) {
            localStorage.setItem("token", data.access_token);
            await fetchAndStoreUser();
            window.location.href = "dashboard.html";
        } else {
            showMessage("msg", data.detail || "Login failed", "error");
        }
    } catch (err) {
        showMessage("msg", "Server error — is backend running?", "error");
    }

    btn.disabled = false;
    btn.textContent = "Login";
}

// ----- FETCH USER INFO -----
async function fetchAndStoreUser() {
    const res = await fetch(`${API}/balance`, {
        headers: { "Authorization": `Bearer ${getToken()}` }
    });
    const data = await res.json();
    localStorage.setItem("account_number", data.account_number);
    localStorage.setItem("username", data.username);
    return data;
}

// ----- DASHBOARD LOAD -----
window.onload = async function () {
    if (!window.location.href.includes("dashboard.html")) return;

    const token = getToken();
    if (!token) {
        window.location.href = "index.html";
        return;
    }

    await loadDashboard();
    startWebSocket();
}

async function loadDashboard() {
    try {
        const res = await fetch(`${API}/balance`, {
            headers: { "Authorization": `Bearer ${getToken()}` }
        });

        if (res.status === 401) {
            logout();
            return;
        }

        const data = await res.json();
        document.getElementById("balance").textContent = parseFloat(data.balance).toFixed(2);
        document.getElementById("account-number").textContent = data.account_number;
        document.getElementById("username").textContent = data.username;

        await fetchTransactions();
    } catch (err) {
        console.error("Dashboard load error:", err);
    }
}

// ----- FETCH TRANSACTIONS -----
async function fetchTransactions() {
    const res = await fetch(`${API}/transactions`, {
        headers: { "Authorization": `Bearer ${getToken()}` }
    });
    const txns = await res.json();
    const tbody = document.getElementById("transactions-body");
    tbody.innerHTML = "";

    if (txns.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;color:#666">No transactions yet</td></tr>`;
        return;
    }

    const myAccount = parseInt(getAccount());

    txns.reverse().forEach(t => {
        const isSent = t.sender_account === myAccount;
        const type = isSent ? "Sent" : "Received";
        const typeClass = isSent ? "sent" : "received";
        const otherAccount = isSent ? t.receiver_account : t.sender_account;
        const date = new Date(t.created_at).toLocaleString();

        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${t.id}</td>
            <td><span class="badge ${typeClass}">${type}</span></td>
            <td>${otherAccount}</td>
            <td>$${parseFloat(t.amount).toFixed(2)}</td>
            <td><span class="badge success">${t.status}</span></td>
            <td>${date}</td>
        `;
        tbody.appendChild(row);
    });
}

// ----- SEND MONEY -----
async function sendMoney() {
    const receiver = document.getElementById("receiver").value;
    const amount = document.getElementById("amount").value;

    if (!receiver || !amount) {
        showMessage("transfer-msg", "Please fill in all fields", "error");
        return;
    }

    if (parseFloat(amount) <= 0) {
        showMessage("transfer-msg", "Amount must be greater than 0", "error");
        return;
    }

    const btn = document.getElementById("send-btn");
    btn.disabled = true;
    btn.textContent = "Sending...";

    const request_id = "txn_" + Date.now();

    try {
        const res = await fetch(`${API}/transfer`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${getToken()}`
            },
            body: JSON.stringify({
                sender_account: parseInt(getAccount()),
                receiver_account: parseInt(receiver),
                amount: parseFloat(amount),
                request_id: request_id
            })
        });
        const data = await res.json();

        if (data.message) {
            showMessage("transfer-msg", `✅ ${data.message} — New balance: $${data.new_balance.toFixed(2)}`, "success");
            document.getElementById("receiver").value = "";
            document.getElementById("amount").value = "";
            await loadDashboard();
        } else {
            showMessage("transfer-msg", data.detail || "Transfer failed", "error");
        }
    } catch (err) {
        showMessage("transfer-msg", "Server error", "error");
    }

    btn.disabled = false;
    btn.textContent = "Send Money";
}

// ----- LOGOUT -----
function logout() {
    localStorage.clear();
    window.location.href = "index.html";
}

// ----- WEBSOCKET -----
function startWebSocket() {
    const account = getAccount();
    if (!account) return;

    const ws = new WebSocket(`ws://18.130.226.110:8000/ws/${account}`);
    ws.onmessage = async function () {
        await loadDashboard();
    }
    ws.onclose = function () {
        setTimeout(startWebSocket, 3000);
    }
}