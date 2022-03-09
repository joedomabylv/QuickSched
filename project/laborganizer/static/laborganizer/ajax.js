$(document).ready(function(){
  $(".switch-btn").click(function(){
    $.ajax({
      url: '/laborganizer/',
      type: 'get',
      data: {
          lab_name: this.id
      },
      success: function(response) {
        for(var key in response) {
          $("#switches-list").append(
            '<a href="#" id="switch" class="list-group-item list-group-item-action switch '+ response[key].score_color + '"> \
              <div class="row align-items-center "> \
                <div class="col-1"> \
                  <h1 class="ms-2 d-flex justify-content-center">' + response[key].switch_id + '</h1> \
                </div> \
              <div class="col"> \
                <div class="d-flex justify-content-center p-2"> \
                  ' + response[key].to_ta + ' (' + response[key].to_lab + ') \
                </div> \
                <div class="d-flex justify-content-center"> \
                  <svg class="bi" width="16" height="16"> \
                    <use xlink:href="#switch"></use> \
                  </svg> \
                </div> \
                <div class="d-flex justify-content-center p-2"> \
                  ' + response[key].from_ta + ' (' + response[key].from_lab + ') <br /> Deviation Score: ' + response[key].deviation_score + '\
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
