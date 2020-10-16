(function ($) {
  'use strict';

  // NAVIGATION
  var responsiveNav = $('#responsive-nav'),
    catToggle = $('#responsive-nav .category-nav .category-header'),
    catList = $('#responsive-nav .category-nav .category-list'),
    menuToggle = $('#responsive-nav .menu-nav .menu-header'),
    menuList = $('#responsive-nav .menu-nav .menu-list');

  catToggle.on('click', function () {
    menuList.removeClass('open');
    catList.toggleClass('open');
  });

  menuToggle.on('click', function () {
    catList.removeClass('open');
    menuList.toggleClass('open');
  });

  $(document).click(function (event) {
    if (!$(event.target).closest(responsiveNav).length) {
      if (responsiveNav.hasClass('open')) {
        responsiveNav.removeClass('open');
        $('#navigation').removeClass('shadow');
      } else {
        if ($(event.target).closest('.nav-toggle > button').length) {
          if (!menuList.hasClass('open') && !catList.hasClass('open')) {
            menuList.addClass('open');
          }
          $('#navigation').addClass('shadow');
          responsiveNav.addClass('open');
        }
      }
    }
  });

  // HOME SLICK
  $('#home-slick').slick({
    autoplay: true,
    infinite: true,
    speed: 300,
    arrows: true,
  });

  // PRODUCTS SLICK
  $('#product-slick-1').slick({
    slidesToShow: 3,
    slidesToScroll: 2,
    autoplay: true,
    infinite: true,
    speed: 300,
    dots: true,
    arrows: false,
    appendDots: '.product-slick-dots-1',
    responsive: [
      {
        breakpoint: 991,
        settings: {
          slidesToShow: 1,
          slidesToScroll: 1,
        },
      },
      {
        breakpoint: 480,
        settings: {
          dots: false,
          arrows: true,
          slidesToShow: 1,
          slidesToScroll: 1,
        },
      },
    ],
  });

  $('#product-slick-2').slick({
    slidesToShow: 3,
    slidesToScroll: 2,
    autoplay: true,
    infinite: true,
    speed: 300,
    dots: true,
    arrows: false,
    appendDots: '.product-slick-dots-2',
    responsive: [
      {
        breakpoint: 991,
        settings: {
          slidesToShow: 1,
          slidesToScroll: 1,
        },
      },
      {
        breakpoint: 480,
        settings: {
          dots: false,
          arrows: true,
          slidesToShow: 1,
          slidesToScroll: 1,
        },
      },
    ],
  });

  // PRODUCT DETAILS SLICK
  $('#product-main-view').slick({
    infinite: true,
    speed: 300,
    dots: false,
    arrows: true,
    fade: true,
    asNavFor: '#product-view',
  });

  $('#product-view').slick({
    slidesToShow: 3,
    slidesToScroll: 1,
    arrows: true,
    centerMode: true,
    focusOnSelect: true,
    asNavFor: '#product-main-view',
  });

  // PRODUCT ZOOM
  $('#product-main-view .product-view').zoom();

  // PRICE SLIDER
  var slider = document.getElementById('price-slider');
  if (slider) {
    noUiSlider.create(slider, {
      start: [1, 999],
      connect: true,
      tooltips: [true, true],
      format: {
        to: function (value) {
          return value.toFixed(2) + '$';
        },
        from: function (value) {
          return value;
        },
      },
      range: {
        min: 1,
        max: 999,
      },
    });
  }
})(jQuery);

$(function () {
  $('#query').autocomplete({
    source: '/search_auto/',
    select: function (event, ui) {
      AutoCompleteSelectHandler(event, ui);
    },
    minLength: 2,
  });
});

function AutoCompleteSelectHandler(event, ui) {
  var selectedObj = ui.item;
}

$(document).ready(function () {
  $('#validationForm').validate({
    rules: {
      first_name: 'required',
      last_name: 'required',
      username: {
        required: true,
        minlength: 6,
      },
      l_username: 'required',
      password: {
        required: true,
        minlength: 6,
      },
      l_password: 'required',
      old_password: 'required',
      confirm_password: {
        required: true,
        equalTo: '#password',
      },
      email: {
        required: true,
        email: true,
      },
      agree: 'required',
    },
    messages: {
      first_name: 'Please enter your first name',
      last_name: 'Please enter your last name',
      username: {
        required: 'Please enter a username',
        minlength: 'Your username must consist of at least 6 characters',
      },
      l_username: 'Please enter a username',
      password: {
        required: 'Please provide a password',
        minlength: 'Your password must be at least 6 characters long',
      },
      l_password: 'Please provide a password',
      old_password: 'Please enter your old password password',
      confirm_password: {
        required: 'Please confirm your password',
        equalTo: 'Please enter the same password as above',
      },
      email: 'Please enter a valid email address',
      agree: 'Please accept our policy',
    },
    errorElement: 'em',
    errorPlacement: function (error, element) {
      error.addClass('help-block');

      if (element.prop('type') === 'checkbox') {
        error.insertAfter(element.parent('label'));
      } else {
        error.insertAfter(element);
      }
    },
    highlight: function (element, errorClass, validClass) {
      $(element)
        .parents('.form-group')
        .addClass('has-error')
        .removeClass('has-success');
    },
    unhighlight: function (element, errorClass, validClass) {
      $(element)
        .parents('.form-group')
        .addClass('has-success')
        .removeClass('has-error');
    },
  });
  if ($.fn.passwordStrength) {
    $('#password').passwordStrength({
      minimumChars: 6,
    });
  }
  $('#fileupload').change(function (event) {
    var x = URL.createObjectURL(event.target.files[0]);
    $('#upload-img').attr('src', x);
    console.log(event);
  });
});


const usernameField = document.querySelector('#usernameField');
const feedBackArea = document.querySelector('.usernameFeedBackArea');
const emailField = document.querySelector('#emailField');
const emailFeedBackArea = document.querySelector('.emailFeedBackArea');

usernameField.addEventListener('keyup', (e) => {
  const usernameVal = e.target.value;
  usernameField.classList.remove('has-error');
  feedBackArea.style.display = 'none';
  if (usernameVal.length > 0) {
    fetch('/authentication/validate_username', {
      body: JSON.stringify({ username: usernameVal }),
      method: 'POST',
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.username_error) {
          usernameField.classList.add('has-error');
          feedBackArea.style.display = 'block';
          feedBackArea.innerHTML = `<p style="color:#a94442";>${data.username_error}</p>`;
        }
      });
  }
});


emailField.addEventListener('keyup', (e) => {
  const emailVal = e.target.value;
  emailField.classList.remove('has-error');
  emailFeedBackArea.style.display = 'none';
  if (emailVal.length > 0) {
    fetch('/authentication/validate_email', {
      body: JSON.stringify({ email: emailVal }),
      method: 'POST',
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.email_error) {
          emailField.classList.add('has-error');
          emailFeedBackArea.style.display = 'block';
          emailFeedBackArea.innerHTML = `<p style="color:#a94442";>${data.email_error}</p>`;
        }
      });
  }
});