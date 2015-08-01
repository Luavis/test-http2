
var options = {plain: true}

require("http2")
    .raw
    .createServer(options,
    function(res, req){
      req.end("Hello World")
    }).listen(8080)

