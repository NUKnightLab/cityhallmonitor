var summaryTemplate = null;
var singleResultTemplate = null;
var multiResultTemplate = null;
var resultStatsTemplate = null;

$(function() {
    summaryTemplate = _.template($("#summary-template").html());
    singleResultTemplate = _.template($("#single-result-template").html());
    multiResultTemplate = _.template($("#multi-result-template").html());
    resultStatsTemplate = _.template($("#result-stats-sidebar").html());
    $('.example-search').click(function() {
        $('#search-input').val($(this).text());
        $('#search-submit').click();
        return false;
    });
    buildDateUI();
});

var appendResult = function(obj) {
    var statusClass;
    switch (obj.docs[0].matter.status){
        case 'Adopted':
        case 'Approved':
        case 'Passed':
        case 'Recommended for Passage':
            statusClass = 'success';
            break;

        case 'Deferred and Published':
        case 'Direct Introduction':
        case 'In Committee':
        case 'Introduced':
        case 'Placed on File':
        case 'Recommended for Re-referral':
        case 'Re-referred':
            statusClass = 'warning';
            break;

        case 'Failed to Pass':
        case 'Recommended Do Not Pass':
        case 'Tabled':
        case 'Vetoed':
        case 'Void':
        case 'Withdrawn':
            statusClass = 'alert';
            break;
    }
    if(obj.docs.length > 1) {
        $(multiResultTemplate({docs: obj.docs, statusClass: statusClass})).appendTo('#search-results');
    } else {
        $(singleResultTemplate({doc: obj.docs[0], statusClass: statusClass})).appendTo('#search-results');
    }
};

//Need to store the results of the AJAX call somewhere so we can sort without hitting the database
var resultData = {
  'documents': [],
  'dateGroups': {},
  'rankGroups': {},
  'sidebarData': {}, //statsData
  'query': '',
  'dateRangeType': '',
  'ignoreRoutine': true,
  'queryQualifier': '',
  'isRanked': false,
  'truncated': false,
  'fullCount': ''
}

function populateResults(sortType){
    typeKeys = Object.keys(resultData[sortType]);
    if (sortType == "dateGroups"){
      typeKeys.sort(function(a,b) { return (b < a) ? -1 : 1 });
    } //Do we also need to sort ranks?
    for (i=0; i<typeKeys.length; i++) {
        var resultGroups = resultData[sortType][typeKeys[i]];
        $.each(resultGroups, function(j, g) {
            appendResult(g);
        });
    }
    //setTimeout(function() { hideNonPages(); }, 3000);
    $(".sort[data-grouptype='" + sortType + "']").children('.option').addClass('active');
    $(".sort[data-grouptype='" + sortType + "']").siblings().children().removeClass('active');
}

function appendSummaryAndStats(total, qualifier, statsData, truncatedFlag, fullCount){
    var query = $('#search-input').val();
    // if ($('#search-input').val() != '') {
    //   query = 'matching <em>' + $('#search-input').val() + '</em>';
    // }
    $('#results-summary').html($(summaryTemplate({
        total: total,
        query: query,
        qualifier: qualifier,
        truncated: truncatedFlag,
        fullCount: fullCount
    })));
    /* not using the sidebar right now */
    //$('#results-stats').empty();
    //if (total > 0) {
        //$('#results-stats').html(resultStatsTemplate({statsData: statsData}));
    //}
}

var doSearch = function(searchUrl, subscribeUrl) {
    showLoadingState();
    resultData = {
      'documents': [],
      'dateGroups': {},
      'rankGroups': {},
      'sidebarData': {}, //statsData
      'query': $('#search-input').val(),
      'dateRangeType': $('#date-range-type input[type="radio"]:checked').val(),
      'ignoreRoutine': $('#ignore-routine').is(':checked'),
      'queryQualifier': '',
      'isRanked': false,
      'truncated': false,
      'fullCount':''
    }
    // only rank if there is a search term
    if (resultData.query != "") {
      resultData.isRanked = true;
    }

    //build up summary stats for sidebar
    function buildResultStats(doc, statsData){
        var statTypes = {
            'Statuses': 'status',
            'Matter Types': 'type'
        };
        $.each(statTypes, function(key, matter_field) {
            if (!(key in statsData)){
                statsData[key] = {};
            }
            if(doc.matter[matter_field] in statsData[key]) {
                statsData[key][doc.matter[matter_field]] += 1;
            } else {
                statsData[key][doc.matter[matter_field]] = 1;
            }
        });
        return statsData;
    };

    // group documents with their related matters
    function buildDateResults(data){
        if(data.documents.length > 0) {
            var dates = [];
            //TODO: create statsData global so we don't have to rebuild sidebar on sort-by-rank?
            $.each(data.documents, function(i, doc) {
                // dt is datetime
                var dt = doc.sort_date;
                // if the datetime hasn't already been added to the dates array
                if(dates.indexOf(dt) < 0) {
                    dates.push(dt);
                    resultData.dateGroups[dt] = {};
                }
                // if the datetime already exists in `groups`, it means the matter has multiple documents: add docs to existing matter
                // otherwise just create the `docs` property
                if(doc.matter.id in resultData.dateGroups[dt]) {
                    resultData.dateGroups[dt][doc.matter.id]['docs'].push(doc);
                } else {
                    resultData.dateGroups[dt][doc.matter.id] = {
                        'docs': [doc]
                    };
                }
                buildResultStats(doc, resultData.sidebarData);
            });
        }
    }

    function buildRankResults(data){
        if(data.documents.length > 0) {
            var ranks = [];
            $.each(data.documents, function(i, doc) {
                var rank = doc.rank;
                if(ranks.indexOf(rank) < 0) {
                    ranks.push(rank);
                    resultData.rankGroups[rank] = {};
                }
                if(doc.matter.id in resultData.rankGroups[rank]) {
                    resultData.rankGroups[rank][doc.matter.id]['docs'].push(doc);
                } else {
                    resultData.rankGroups[rank][doc.matter.id] = {
                        'docs': [doc]
                    };
                }
            });
        }
    }

    function showEmailForm(){
      $('#search-subscribe-form').show();
      $('#search-subscribe-form').submit(function(event) {
          handle_subscribe(event, subscribeUrl);
          return false;
      });
    }

    function showSortButtons(){
      $('#sort-by').show();
    }

    //used to determine language to display and time period to return
    var preposition = ' from '; // just a little nuance to the qualifier language
    if (resultData.query) {
      preposition = ' in ';
    }
    switch (resultData.dateRangeType) {
        case 'past-year':
            resultData.queryQualifier = preposition + 'the past year';
            break;

        case 'past-month':
            resultData.queryQualifier = preposition + 'the last 30 days';
            break;

        case 'any':
            break;
    }

    $.ajax({
        url: searchUrl,
        data: {
            query: resultData.query,
            date_range: resultData.dateRangeType,
            ignore_routine: resultData.ignoreRoutine,
            is_ranked: resultData.isRanked,
            resultData: resultData.truncated,
            fullCount: resultData.fullCount
        }
    })
    .success(function(data) {
        resultData.truncated = data.truncated;
        resultData.fullCount = data.full_count;
        resultData.documents = data.documents;
        buildDateResults(data);
        appendSummaryAndStats(resultData.documents.length, resultData.queryQualifier, resultData.sidebarData, resultData.truncated, resultData.fullCount);
        if (data.is_ranked) {
          //NOTE: are results in ranked order already? If so, we just need to create meta.
          buildRankResults(data);
          populateResults("rankGroups");
        } else {
          populateResults("dateGroups");
        }

        if (resultData.query != '') {
          // don't let people subscribe to queries without keywords
          showEmailForm(subscribeUrl);
        }
        if (resultData.documents.length > 0 && resultData.isRanked) {
          showSortButtons();
        }
        $("#search-results").foundation('reveal', 'reflow');

    })
    .error(function(xhr, status, errMsg) {
        alert(errMsg);
    })
    .complete(function(xhr, status) {
        hideLoadingState();
    });
}; // doSearch

$('#sort-by .sort').on('click', function(){
  if (resultData.documents.length > 0){
    $('#search-results').empty();
    populateResults($(this).data('grouptype'));
  }
});
