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
      if (req.status == 401) {
        alert(contents['error']);
        document.getElementById('password').focus();
      }
      else
      {

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

