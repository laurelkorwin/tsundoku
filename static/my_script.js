
//Script for form input on search page - sets form inputs for relevant book when button is clicked.
$('.book_result').click(
      function(){

      var title = $(this).data('title');
      $('#title').val(title);

      var author = $(this).data('author');
      $('#author').val(author);

      var asin = $(this).data('asin');
      $('#asin').val(asin);

      var md_image = $(this).data('md-image');
      $('#md_image').val(md_image);

      var lg_image = $(this).data('lg-image');
      $('#lg_image').val(lg_image);

      var url = $(this).data('url');
      $('#url').val(url);

      var numPages = $(this).data('num-pages');
      $('#num_pages').val(numPages);
      debugger;

      var primaryNodeID = $(this).data('primary-node-id');
      $('#primary_node_id').val(primaryNodeID);

      var primaryNode = $(this).data('primary-node');
      $('#primary_node').val(primaryNode);

      var parentNodeID = $(this).data('parent-node-id');
      $('#parent_node_id').val(parentNodeID);

      var parentNode = $(this).data('parent-node');
      $('#parent_node').val(parentNode);


  });

$('.friend_book').click(
      function(){

      var title = $(this).data('title');
      $('#title').val(title);

      var author = $(this).data('author');
      $('#author').val(author);

      var asin = $(this).data('asin');
      $('#asin').val(asin);

      var md_image = $(this).data('md-image');
      $('#md_image').val(md_image);

      var lg_image = $(this).data('lg-image');
      $('#lg_image').val(lg_image);

      var url = $(this).data('url');
      $('#url').val(url);


  });

// Functions to update "read" status on board details page with AJAX

function updateHTML(results){

      // sets book id equal to the value in results dict
      var book_id = results.book_id;
      // puts in HTML stating that user has read book before div with the same id as book id
      $('<span class="glyphicon glyphicon-ok" aria-hidden="true"></span> Read').insertBefore('#' + book_id);
      // hides div with id of book id
      $('#' + book_id).hide();
}

function sendReadToDB (){
            
            // sets book id variable equal to the book id data for the particular button clicked
            var book_id = $(this).data('book-id');
            // sends a post request to the read book route, providing book id
            // when returning from server, calls updateHTML function
            $.post('/read_book', {'book_id': book_id}, updateHTML);
      }

// Functions to update "rating" status on board details page with AJAX

// simple function to multiply a string by a certain number
// creates a blank array with length of 1 greater than the number, and then joins with the string as the "joiner"
function repeat(str, num) {
    return (new Array(num + 1)).join(str);
}

function updateRating(results) {

      // sets asin equal to the value in results dict
      var asin = results.asin;
      // sets rating equal to an integer of the score in results dict
      var rating = parseInt(results.score);
      // sets stars equal to the below span, multiplied by the rating value
      var stars = repeat('<span class="glyphicon glyphicon-star" aria-hidden="true"></span>', rating);
      // inserts 'Rating' and stars before the div with ID of the asin
      $('<p>Rating: ' + stars + '</p>').insertBefore('#' + asin); //fix this eventually - stars are sad looking and droopy :(
      // hides div with id asin
      $('#' + asin).hide();
}

function sendRatingToDB(evt){

      evt.preventDefault();
      // prevents default form submission

      var book_id = $(this).data('book-id');
      // gets book id from book id data for the particular button clicked

      var score = $('input[name="rating"]:checked').val();
      // gets score from whatever rating input the user checked

      $.post('/rate_book', {'book_id': book_id, 'score': score}, updateRating);
      // sends post request to /rate_book route, passing in book id and score. 
      // calls updateRating function upon return
}

// sets event listener for "mark read" buttons
$('.mark_read').click(sendReadToDB);

// sets event listener for "rate" buttons
$('.rate_book').click(sendRatingToDB);



$('.grid').masonry({
  // options...
  itemSelector: '.grid-item',
  columnWidth: 200
});