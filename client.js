
var fs = require('fs');
var path = require('path');
var http2 = require('http2');

// We use self signed certs in the example code so we ignore cert errors
process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";

// Sending the request
var url = 'https://localhost:8000/'
var request = http2.get(url);

// Receiving the response
request.on('response', function(response) {
  response.pipe(process.stdout);
  // console.log(arguments)
  // response.on('end', finish);
});

request.on('error', function() {
  console.log(arguments)
});

// Receiving push streams
request.on('push', function(pushRequest) {
  console.log(arguments)
});

// Quitting after both the response and the associated pushed resources have arrived
var push_count = 0;
var finished = 0;
function finish() {
  finished += 1;
  if (finished === (1 + push_count)) {
    process.exit();
  }
}
