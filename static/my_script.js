
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

      var primaryNodeID = $(this).data('primary-node-id');
      $('#primary_node_id').val(primaryNodeID);

      var primaryNode = $(this).data('primary-node');
      $('#primary_node').val(primaryNode);

      var parentNodeID = $(this).data('parent-node-id');
      $('#parent_node_id').val(parentNodeID);

      var parentNode = $(this).data('parent-node');
      $('#parent_node').val(parentNode);


  });

function deleteBook() {
      var book_id = $(this).data('book-id');
      var master_div = $(this).parent().parent().parent();

      $.post('/delete_book', {'book_id': book_id}, function(results){

            $(master_div).hide();
      });
}

$('.delete-book').click(deleteBook);

// SETS BOOK ID IN MODAL FORM USING DATA ON BUTTON THAT WAS CLICKED

function setModalBookID(){
      var book_id = $(this).data('book-id');
      $('#book_id').val(book_id);
}

$('.friend_book').click(setModalBookID);

function updateFriendDiv(results){
      var potentials = results.possible_friends;
      $('#friends_to_rec').empty();

      if (potentials.length === 0) {
            $('#friends_to_rec').html("<p>Looks like you've already recommended this book to all your friends!</p>");
            debugger;
            $('#recommend_notes').hide();
      }

      else { for (var i = 0; i < potentials.length; i++){
            $('#friends_to_rec').append('<p>Which friend(s) would you like to recommend this book to?</p> <input type="checkbox" name="friend" value="'+ potentials[i][1] + '"> ' + potentials[i][0] + '<br>');
            $('#recommend_notes').show();
      }
      }
}

$('.recommend_book').click(function(){

      var book_id = $(this).data('book-id');
      $('#book_id').val(book_id);

      $.get('/get_rec_friends', {'book_id': book_id}, updateFriendDiv);

});

// FUNCTIONS TO SHOW NOTES FOR EACH BOOK

function showNotes(results){

      // sets notes variable according to the result sent back from the server
      var notes = results.notes;

      // if notes exist, populate modal with textarea containing current notes and give user the ability to edit
      // otherwise, populate modal with blank textarea and give user the ability to add
      if (notes[0] !== null && notes[0] !== '') {
            $('#notes').html("<p>Your current notes:</p> <textarea id='book_notes' rows='8' cols='50' name='notes'>" + notes + "</textarea>");
            $('#submit_button').val('Edit');
      } else {
            $('#notes').html("<p>Add notes:</p> <textarea id='book_notes' rows='8' cols='50' name='notes' placeholder='Add notes'></textarea>");
            $('#submit_button').val('Add');
      }
}

// upon clicking the notes button, set modal window rating-id form input equal to that book's rating id
// also, send get request to server for any notes associated with that rating
$('.see_notes').click(
      function(){
            var rating_id = $(this).data('rating-id');
            $('#rating_id').val(rating_id);

            $.get('/get_notes', {'rating_id': rating_id}, showNotes);
});


// RECOMMENDATION FUNCTIONALITY - ACCEPT AND IGNORE
// sets book id and recommendation id on modal window form for the selected book
$('.accept_rec').click( function(){

      var book_id = $(this).data('book-id');
      $('#book_id').val(book_id);

      var rec_id = $(this).data('rec-id');
      $('#rec_id').val(rec_id);

});

// hides ignored recommendation when data comes back from the server
function hideDiv(results){

      var div_id = results.rec_id;

      $('#'+div_id+'').hide();

}

// upon clicking the 'ignore' button, sends data with book id and rec id to the server
$('.ignore_rec').click(function(){

            var book_id = $(this).data('book-id');
            var rec_id = $(this).data('rec-id');

            $.post('/ignore_rec', {'book_id': book_id, 'rec_id': rec_id}, hideDiv);

      });

// FUNCTIONS TO UPDATE READ STATUS

function sendReadToDB (){
            
            // sets book id variable equal to the book id data for the particular button clicked
            var book_id = $(this).data('book-id');
            var that = this;
            var glyph = $(this).prev();
            debugger;
            
            // sends a post request to the read book route, providing book id
            // when returning from server, calls updateHTML function
            $.post('/read_book', {'book_id': book_id}, function (results){
                  debugger;
                  $('<span class="glyphicon glyphicon-ok" aria-hidden="true"></span>').insertBefore($(that));
                  $(that).hide();
                  $(glyph).hide();

            });
      }

// sets event listener for "mark read" buttons
$('.mark_read').click(sendReadToDB);

// FUNCTIONS TO UPDATE RATINGS SCORE

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

// sets event listener for "rate" buttons
$('.rate_book').click(sendRatingToDB);

