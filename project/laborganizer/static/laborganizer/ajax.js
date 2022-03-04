$(document).ready(function(){
  $(".switch-btn").click(function(){
    $.ajax({
      url: '',
      type: 'get',
      data: {
          lab_name: this.id
      },
      success: function(response) {
        for(var key in response) {
          $("#switches-list").append(
            '<a href="#" id="switch" class="list-group-item list-group-item-action switch"> \
              <div class="row align-items-center "> \
                <div class="col-1"> \
                  <h1 class="ms-2 d-flex justify-content-center">1</h1> \
                </div> \
              <div class="col"> \
                <div class="d-flex justify-content-center p-2"> \
                  ' + response[key].TA1 + ' (' + response[key].lab1 + '-' + response[key].section1 + ') Score: ' + response[key].score1 + '\
                </div> \
                <div class="d-flex justify-content-center"> \
                  <svg class="bi" width="16" height="16"> \
                    <use xlink:href="#switch"></use> \
                  </svg> \
                </div> \
                <div class="d-flex justify-content-center p-2"> \
                  ' + response[key].TA2 + ' (' + response[key].lab2 + '-' + response[key].section2 + ') Score: ' + response[key].score2 + '\
                </div> \
              </div> \
            </div> \
              </a>'
          )
        }
      }
    });
  });
});

$(document).ready(function(){
  $(document).on('click', 'a.switch', (function(){
    $.ajax({
      url: '',
      type: 'get',
      data: {
        swap: $(this).children().text()
      },
      success: function(response) {
        $(".close-switches").trigger('click');
        location.reload();
      }
    });
  }));
});

$(document).ready(function(){
  $(document).on('click', 'button.undo', (function(){
    $.ajax({
      url: '',
      type: 'get',
      data: {
        undo: $(this).val()
      },
      success: function(response) {
        $(".close-history").trigger('click');
        location.reload();
      }
    });
  }));
});

$(document).ready(function(){
  $(".close-switches").click(function(){
    $("#switches-list").empty();
  });
});
