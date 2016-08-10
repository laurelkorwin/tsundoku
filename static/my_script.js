$('.book_result').click(
      function(){

      title = $(this).data('title');
      $('#title').val(title);
      console.log(title);

      author = $(this).data('author');
      $('#author').val(author);
      console.log(author);

      asin = $(this).data('asin');
      $('#asin').val(asin);
      console.log(asin);

      md_image = $(this).data('md-image');
      $('#md_image').val(md_image);
      console.log(md_image);

      lg_image = $(this).data('lg-image');
      $('#lg_image').val(lg_image);
      console.log(lg_image);

      url = $(this).data('url');
      $('#url').val(url);
      console.log(url);


  });

