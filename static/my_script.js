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


  });

function updateHTML(results){
      var book_id = results.book_id;
      $('<span class="glyphicon glyphicon-ok" aria-hidden="true"></span> You\'ve read this book! <br>').insertBefore('#' + book_id);
      $('#' + book_id).hide();
}

function sendReadToDB (){
            
            var book_id = $(this).data('book-id');
            console.log(book_id);
            $.post('/read_book', {'book_id': book_id}, updateHTML);
      }

function repeat(str, num) {
    return (new Array(num + 1)).join(str);
}

function updateRating(results) {

      var asin = results.asin;
      var rating = parseInt(results.score);
      var stars = repeat('<span class="glyphicon glyphicon-star" aria-hidden="true">', rating);
      $('<p>Rating: ' + stars + '</p>').insertBefore('#' + asin); //fix this eventually - stars are sad looking and droopy :(
      $('#' + asin).hide();

}

function sendRatingToDB(evt){

      evt.preventDefault();

      var book_id = $(this).data('book-id');

      var score = $('input[name="rating"]:checked').val();

      $.post('/rate_book', {'book_id': book_id, 'score': score}, updateRating);

}

$('.mark_read').click(sendReadToDB);

$('.rate_book').click(sendRatingToDB);