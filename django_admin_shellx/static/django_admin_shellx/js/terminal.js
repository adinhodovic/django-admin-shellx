import { Terminal } from "xterm";
import { FitAddon } from "@xterm/addon-fit";
import { SearchAddon } from "@xterm/addon-search";
import { WebLinksAddon } from "@xterm/addon-web-links";

// TODO: fix webpack > tailwind > postcss
// import "../css/terminal.css";

const status = document.getElementById("djw_status");
const terminal_el = document.getElementById("djw_terminal");

var ws;

const room = Math.floor(Math.random() * 100000) + 1;

function connect() {
  const url =
    "ws://" + window.location.host + "/ws/terminal/" + room.toString() + "/";
  ws = new WebSocket(url);

  ws.onopen = function (event) {
    status.innerHTML = "Connected";
    status.style.color = "green";
    terminal_el.hidden = false;
  };

  ws.onclose = function (event) {
    const code = event.code;

    if (code === 4403 || code === 4404) {
      status.innerHTML =
        "Disconnected - " +
        "Unauthenticated user" +
        " - status code: " +
        code +
        " will not try to reconnect, please ensure to authenticate.";
      status.style.color = "red";
      return;
    }
    status.innerHTML = "Disconnected";
    status.style.color = "red";
    terminal.clear();
    terminal_el.hidden = true;
    setTimeout(function () {
      connect();
    }, 1000);
  };

  ws.onerror = function (event) {
    status.innerHTML = "Error";
    status.style.color = "red";
    ws.close();
  };

  ws.onmessage = function (event) {
    const json_data = JSON.parse(event.data);
    terminal.write(json_data["message"]);
  };
}

connect();

var terminal = new Terminal({
  convertEol: true,
  fontFamily: "Menlo, Monaco, Courier New, monospace",
  bellStyle: "sound",
  fontSize: 15,
  fontWeight: 400,
  cursorBlink: true,
});

terminal.options = {
  theme: {
    background: "#333",
  },
};

const fitAddon = new FitAddon();
terminal.loadAddon(fitAddon);
const searchAddon = new SearchAddon();
terminal.loadAddon(searchAddon);
const webLinksAddon = new WebLinksAddon();
terminal.loadAddon(webLinksAddon);

function sendMessage(msg) {
  // Wait until the state of the socket is not ready and send the message when it is...
  if (ws.readyState !== 1) {
    waitForSocketConnection(ws, function () {
      ws.send(msg);
    });
  } else {
    ws.send(msg);
  }
}

// Make the function wait until the connection is made...
function waitForSocketConnection(socket, callback) {
  setTimeout(function () {
    if (socket.readyState === 1) {
      if (callback != null) {
        callback();
      }
    } else {
      waitForSocketConnection(socket, callback);
    }
  }, 100); // wait 100 milisecond for the connection...
}

terminal.onData((data) => {
  const json_data = JSON.stringify({
    action: "input",
    data: {
      message: data,
    },
  });
  sendMessage(json_data);
});

function resize(size) {
  const json_data = JSON.stringify({
    action: "resize",
    data: {
      cols: size.cols,
      rows: size.rows,
    },
  });
  sendMessage(json_data);
}

function fitToscreen() {
  fitAddon.fit();
  const dims = { cols: terminal.cols, rows: terminal.rows };
  resize(dims);
}

function debounce(func, wait_ms) {
  let timeout;
  return function (...args) {
    const context = this;
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(context, args), wait_ms);
  };
}

terminal.onResize((size) => {
  resize(size);
});

terminal.open(terminal_el);
fitAddon.fit();
terminal.resize(10, 30);
fitAddon.fit();

//  ctrl + c for copy when selecting data, default otherwise
terminal.attachCustomKeyEventHandler((arg) => {
  if (arg.ctrlKey && arg.code === "KeyC" && arg.type === "keydown") {
    const selection = terminal.getSelection();
    if (selection) {
      copyText(selection);
      return false;
    }
  }
  return true;
});

function sendHistory(command, prompt = null) {
  var commandStripped = null;
  if (command) {
    commandStripped = command.trim();
  }
  const json_data = JSON.stringify({
    action: "save_history",
    data: {
      command: commandStripped,
      prompt: prompt,
    },
  });
  sendMessage(json_data);
}

// Sends history on the current line to server
function extractHistorySend() {
  // get the current command
  const currentCommand = terminal._core.buffer.lines
    .get(terminal._core.buffer.ybase + terminal._core.buffer.y)
    .translateToString();

  var command = null;
  var prompt = null;
  // strip everything before $ or >>>
  if (currentCommand.startsWith(">>>")) {
    const match = currentCommand.match(/>>>(.*)/);
    command = match ? match[1] : null;
    prompt = "django-shell";
  } else {
    const regex = /^(\S+\s+[^$]+\$)\s+(.*)/;
    const match = currentCommand.match(regex);
    command = match ? match[2] : null;
    prompt = "shell";
  }

  sendHistory(command, prompt);
}

// Enter to send command history
terminal.attachCustomKeyEventHandler((arg) => {
  if (arg.code === "Enter" && arg.type === "keydown") {
    extractHistorySend();
    return true;
  }
});

function copyTextToClipboard(event) {
  navigator.clipboard.writeText(event.target.dataset.command);
}

var copyButtons = document.querySelectorAll("#djw_copy_command");
copyButtons.forEach((button) => {
  button.addEventListener("click", copyTextToClipboard);
});

var commandHistoryTabs = document.querySelectorAll("#djw_command_history_tab");
commandHistoryTabs.forEach((button) => {
  // Event listener that removes the class tab-active
  button.addEventListener("click", function (event) {
    var tab = event.target;
    var tabs = document.querySelectorAll("#djw_command_history_tab");
    tabs.forEach((tab) => {
      tab.classList.remove("tab-active");
    });
    var tables = document.querySelectorAll(".djw_command_history_table");
    tables.forEach((table) => {
      // Check if table has the id of the table
      if (table.id === tab.dataset.table) {
        table.classList.remove("hidden");
      } else {
        table.classList.add("hidden");
      }
    });
    tab.classList.add("tab-active");
  });
});

function executeCommand(event) {
  const command = event.target.dataset.command;
  if (command) {
    terminal.write(command + "\r");
    const json_data = JSON.stringify({
      action: "input",
      data: {
        message: command + "\r",
      },
    });

    sendMessage(json_data);
    sendHistory(command);
  }
}

var executeButtons = document.querySelectorAll("#djw_execute_command");
executeButtons.forEach((button) => {
  button.addEventListener("click", executeCommand);
});

const wait_ms = 50;
window.onresize = debounce(fitToscreen, wait_ms);
