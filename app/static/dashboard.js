// A helper function for making JSON AJAX requests
function request(method, url, data, callback) {
  var xhr = new XMLHttpRequest();
  xhr.onreadystatechange = function() {
    if (xhr.readyState === this.DONE) {
      var body = null;
      if (this.responseText != null) {
        body = JSON.parse(this.responseText);
      }
      // TODO perhaps handle errors here
      callback(this.status, body);
    }
  }
  xhr.open(method, url);
  if (data != null) {
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send(JSON.stringify(data));
  }
}

// A helper function for creating DOM nodes in a clean way
function node(tagName /*, ...children */) {
  var result = document.createElement(tagName);

  for (var i = 1; i < arguments.length; i ++) {
    var child = arguments[i];
    if (typeof(child) === 'string') {
      result.appendChild(document.createTextNode(child));
    } else {
      result.appendChild(child);
    }
  }

  return result;
}

// A helper function for clearing a DOM node's children
function clear(node) {
  while (node.firstChild) {
      node.removeChild(node.firstChild);
  }
}

function showEndpoints() {
  if (window.endpoints == null) return;
  // Sort the endpoints by name
  endpoints.sort(function(a, b) {
    return a.name.localeCompare(b.name);
  });

  // Shove them into the table
  var tbody = document.getElementById('endpoint-list');
  clear(tbody);
  endpoints.forEach(function(endpoint) {
    var tr = node('tr', 
      node('td', endpoint.name),
      node('td',
        node('code', endpoint.token)),
      node('td',
        endpoint.disabled ? 'N' : 'Y'));
    tr.data_id = endpoint.id;
    tr.onclick = function() {
      window.selectedEndpointId = endpoint.id;
      showSelectedEndpoint();
    };

    tbody.appendChild(tr);
  });

  // Select the first one if none is selected
  if (window.selectedEndpointId == null && endpoints.length) {
    window.selectedEndpointId = endpoints[0].id;
  }

  showSelectedEndpoint();
}

function showSelectedEndpoint() {
  if (window.selectedEndpointId == null) return;

  // Select the row in the table
  var tbody = document.getElementById('endpoint-list');

  for (var i in tbody.childNodes) {
    var tr = tbody.childNodes[i];
    tr.className = (tr.data_id === window.selectedEndpointId) ? 'selected' : '';
  }

  var endpoint = window.endpoints.filter(function(e) {
    return e.id === window.selectedEndpointId
  })[0];

  // Fill the token boxes in the example code
  var tokenBoxes = document.getElementsByClassName('endpt-token');
  for (var i = 0; i < tokenBoxes.length; ++ i) {
    var box = tokenBoxes[i];
    clear(box);
    box.appendChild(document.createTextNode(endpoint.token)); // TODO broken
  }

  randomizeReqIds();
}

function randomizeReqIds() {
  var reqidBoxes = document.getElementsByClassName('reqid');
  for (var i = 0; i < reqidBoxes.length; ++ i) {
    var box = reqidBoxes[i];
    clear(box);
    box.appendChild(document.createTextNode(Math.floor(Math.random() * 100000))); // TODO broken
  }
}

function createClicked() {
  var input = document.getElementById('new-endpoint-name');

  request('POST', '/ui/endpoints', {name: input.value}, function(status, resp) {
    console.log(status);
    window.endpoints.push(resp);
    window.selectedEndpointId = resp.id;
    showEndpoints();
  });

  input.value = '';
}

window.onload = function() {
  document.getElementById('create-button').onclick = createClicked;
  document.getElementById('new-endpoint-name').onkeyup = function(e) {
    if (e.keyCode === 13) {
      createClicked();
      return false;
    }
  }

  // Start randomly updating reqid boxes every five seconds, just to show that
  // the content of the _reqid field doesn't matter
  setInterval(randomizeReqIds, 5000);
};
