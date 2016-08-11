$('.book_result').click(
      function(){

      title = $(this).data('title');
      $('#title').val(title);

      author = $(this).data('author');
      $('#author').val(author);

      asin = $(this).data('asin');
      $('#asin').val(asin);

      md_image = $(this).data('md-image');
      $('#md_image').val(md_image);

      lg_image = $(this).data('lg-image');
      $('#lg_image').val(lg_image);

      url = $(this).data('url');
      $('#url').val(url);


  });


