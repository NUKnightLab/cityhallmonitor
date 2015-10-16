$ = jQuery;

var handle_subscribe = function(event, url) {
    var email = $('#search-subscribe-email').val().trim();
    if(!email) {
        $('#post-subscribe-msg').fadeIn('slow')
                                .text('You must enter your email address.');
        return;
    }
    var query = $('#search-input').val().trim();
    if(!query) {
        alert('You must enter a search query');
        return;
    }

    $.ajax({
        url: url,
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
                $('#post-subscribe-msg').fadeIn('slow')
                                        .text('Error making subscription: '+ data.error);
            } else {
                $('#post-subscribe-msg').fadeIn('slow')
                                        .text('We sent you an email. Click the link in it to confirm your subscription.');
            }
        }
    });
}

var buildDateUI = function(){
  $('#date').on('change', 'select', function(){
    if ($('#date option:selected').val() == 'date-range'){
      $('.custom-date-start, .custom-date-end').slideDown();
    } else {
      $('.custom-date-start, .custom-date-end').slideUp();
    }
  });
}

var showLoadingState = function(){
    $('#spinner-holder').show();
    $('#results-summary, #search-results').html('');
    $('input, button, select').prop('disabled', true);
    $("#search-submit").html("Loading");
    //$('#big-hed').slideUp();
};

var hideLoadingState = function(){
    $('#spinner-holder').hide();
    $("#search-submit").html("Search");
    //$("#facets").removeClass('hide');
    $('input, button, select').prop('disabled', false);
};

$(function() {
    $(document).foundation();

    // Load DC viewer into modal after opened, else positioned incorrectly
    $(document).on('opened.fndtn.reveal', '[data-reveal]', function () {
        var documentId = $('#document-modal').data('chm-doc-id');

        DV.load('https://www.documentcloud.org/documents/'+documentId+'.js', {
            container : '#document-modal-view',
            responsive: true
        });
    });

    // Unload DC viewer when modal is closing
    $(document).on('close.fndtn.reveal', '[data-reveal]', function () {
        for(var key in DV.viewers) {
            DV.viewers[key].api.unload();
        }
    });

    $('#search-results').on('click', 'a.read-more', function(evt) {
        evt.preventDefault();

        $('#document-modal-view').html('');

        $('#document-modal').foundation('reveal', 'open')
            // Store document id in modal data for DV.load
            .data('chm-doc-id', $(this).attr('data-document'));
    });
});
