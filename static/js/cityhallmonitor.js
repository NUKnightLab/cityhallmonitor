$ = jQuery;

function handle_subscribe(event) {
    var email = $('#search-subscribe-email').val().trim();
    if(!email) {
        alert('You must enter your email address');
        return;
    }
    var query = $('#search-input').val().trim();
    if(!query) {
        alert('YOu must enter a search query');
        return;
    }

    $.ajax({
        url: '{% url "subscribe" %}',
        type: 'GET',
        data: {email: email, query: query},
        cache: false,
        dataType: 'json',
        timeout: 20000,
        error: function(xhr, status, err) {
            alert('Error making subscription: '+err);
        },
        success: function(data) {
            if(data.error) {
                alert('Error making subscription: '+data.error);
            } else {
                alert('Ok, you should get an email');
            }
        }
    });
}

function buildDateUI(){
  $('#date').on('change', 'select', function(){
    if ($('#date option:selected').val() == 'date-range'){
      $('.custom-date-start, .custom-date-end label').slideDown();
    } else {
      $('.custom-date-start, .custom-date-end').slideUp();
    }
  });
  $('#end-date-trigger').on('click', function(){
    $('.custom-date-end form').slideToggle();
    $('.custom-date-end').toggleClass('visible');
  });
}

$(function() {
    $('#results-summary').on('change', '#email-checkbox', function(){
      if ($(this).is(':checked')){
        $('#search-subscribe-form').show();
      } else {
        $('#search-subscribe-form').hide();
      }
    });
    var summaryTemplate = _.template($("#summary-template").html());
    var resultTemplate = _.template($("#result-template").html());


    var addResult = function(obj) {
        $.each(obj.docs, function(i, doc) {
            $(resultTemplate(doc)).appendTo('#search-results');
        });
    };

    var doSearch = function() {
        $('#results-summary, #search-results').html('');
        $('#results-progress').show();

        var q = $('#search-input').val();
        q = q + ' account:12872-knight-lab project:"Chicago City Hall Monitor"';
        $.ajax({
            url: 'https://www.documentcloud.org/api/search.json?q=' + q + '&per_page=1000&data=true'
        })
        .success(function(data) {
            var groups = {};

            $.each(data.documents, function(i, doc) {
                if(doc.data.MatterId in groups) {
                    groups[doc.data.MatterId]['docs'].push(doc);
                } else {
                    groups[doc.data.MatterId] = {
                        'data': doc.data,
                        'docs': [doc]
                    };
                }
            });

            $('#results-summary').html($(summaryTemplate(data)));

            $('#search-subscribe-form').submit(function(event) {
                handle_subscribe(event);
                return false;
            });

             if(data.documents.length) {
                $.each(groups, function(i, g) {
                    addResult(g);
                });
            }
            $('#results-progress').hide();
        });
    };

    $('#search-form').submit(function() {
        doSearch();
        return false;
    });

    $('.example-search').click(function() {
        console.log($(this).text());
        $('#search-input').val($(this).text());
        $('#search-submit').click();
        return false;
    });

    buildDateUI();
});
