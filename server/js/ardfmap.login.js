/* A leaflet plugin for providing a login/logout button.
  Copyright (c) 2013, Sean Donnellan
*/

function LoginCommand() {
  //alert("the user wants to login.");
  var data = {
    'username': L.DomUtil.get('username').value,
    'password': L.DomUtil.get('password').value,
    };

  var req = new XMLHttpRequest();
  req.open('POST', '/api/login', true);
  req.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
  req.onload = function(ev) {
    var contents = JSON.parse(req.responseText);
    if (req.readyState == 4) {
      if (req.status == 401 || req.status == 400) {
        alert(contents.error.message);
        document.getElementById('password').focus();
      } else if (req.status === 200) {
        document.getElementById('ardfmap-login').innerHTML =
          'Logged in as ' + data.username;
      } else {
        alert('An unknown error has occurred during login.');
      }
    }
  }
  req.send(JSON.stringify(data));
}

L.Control.Login = L.Control.extend({
  options: {
    position: 'topright',
  },

  onAdd: function (map) {
    var loginDiv = L.DomUtil.create('div', 'leaflet-control');
    var controlUI = L.DomUtil.create('div', 'leaflet-control-login-interior', loginDiv);
    controlUI.id = "ardfmap-login";
    controlUI.title = 'Login';

    var username = L.DomUtil.create('input', 'username', controlUI);
    username.id = 'username';
    username.placeholder = 'Username';
    var password = L.DomUtil.create('input', 'password', controlUI);
    password.id = 'password';
    password.type = 'password';
    password.placeholder = 'Password';

    // Create an actual login button.
    var button = L.DomUtil.create('a', 'leaflet-control-login-button', controlUI);
    button.innerHTML = "Login";
    L.DomEvent
        .addListener(button, 'click', L.DomEvent.stopPropagation)
        .addListener(button, 'click', L.DomEvent.preventDefault)
    .addListener(button, 'click', function () { LoginCommand(); });
    return loginDiv;
  }
});

