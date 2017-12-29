Network = {
  connect: function(url, headers, callback, type, error, beforeSend) {
      if(error != null && !(error instanceof Function)) {
          console.error("Error hook should be an instance of Function");
          return;
      }

      if(type !== "POST" && type !== "GET") {
          type = "POST";
      }

      $.ajax({
          type: type == null? "POST": "GET",
          url: url,
          headers: headers,
          error: error == null? function() {
              alert("网络错误!");
          }: error,
          beforeSend: beforeSend == null? function() {

          }: beforeSend,
          success: callback
      });
  }
};