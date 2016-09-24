// ----------------------------------------------
// # Search
// ----------------------------------------------
function templateoption(cls,img)
{
	$('body').removeClass('green');
	$('body').removeClass('gold');
	$('body').removeClass('red');
	$('body').removeClass('black');
	$('body').removeClass('dark');
    $('img').removeClass('active');
	
    $('body').addClass(cls);
    $(img).addClass('active');
    $('.opt').addClass('open');
		
}
!function($) {
    "use strict";

(function () {

	
	$('.ti-settings').on('click', function () {
		$(".adminoption").toggle();
	 });
$('.layout').on('click', function () {
	if($(this).val()=="box")
	{
		$('body').addClass('box-layout');
	}
	else
	{
		$('body').removeClass('box-layout');
	}
  });
  
  $('.menu').on('click', function () {
	$('body').removeClass('normal');
	$('body').removeClass('icon-menu');
	$('body').removeClass('top');
		$('body').addClass($(this).val());
	
  });
  

    $('.fa-search').on('click', function () {
        $('.search').fadeIn(500, function () {
            $(this).toggleClass('search-toggle');
        });
    });

    $('.search-close').on('click', function () {
        $('.search').fadeOut(500, function () {
            $(this).removeClass('search-toggle');
        });
    });

}());


$(document).ready(function () {

    // Add body-small class if window less than 768px
    if ($(this).width() < 769) {
        $('body').addClass('body-small');
    } else {
        $('body').removeClass('body-small');
    }

    // MetsiMenu
    $('#side-menu').metisMenu();

    // Minimalize menu
	$('.navbar-minimalize').on('click', function () {
  
        $("body").toggleClass("mini-navbar");


    });
              $(".nano").nanoScroller();
});


// Panels
(function ($) {

    $(function () {
        $('.panel')
                .on('panel:toggle', function () {
                    var $this,
                            direction;

                    $this = $(this);
                    direction = $this.hasClass('panel-collapsed') ? 'Down' : 'Up';

                    $this.find('.panel-body, .panel-footer')[ 'slide' + direction ](200, function () {
                        $this[ (direction === 'Up' ? 'add' : 'remove') + 'Class' ]('panel-collapsed')
                    });
                })
                .on('panel:dismiss', function () {
                    var $this = $(this);

                    if (!!($this.parent('div').attr('class') || '').match(/col-(xs|sm|md|lg)/g) && $this.siblings().length === 0) {
                        var $row = $this.closest('.row');
                        $this.parent('div').remove();
                        if ($row.children().length === 0) {
                            $row.remove();
                        }
                    } else {
                        $this.remove();
                    }
                })
                .on('click', '[data-panel-toggle]', function (e) {
                    e.preventDefault();
                    $(this).closest('.panel').trigger('panel:toggle');
                })
                .on('click', '[data-panel-dismiss]', function (e) {
                    e.preventDefault();
                    $(this).closest('.panel').trigger('panel:dismiss');
                })
                /* Deprecated */
                .on('click', '.panel-actions a.fa-caret-up', function (e) {
                    e.preventDefault();
                    var $this = $(this);

                    $this
                            .removeClass('fa-caret-up')
                            .addClass('fa-caret-down');

                    $this.closest('.panel').trigger('panel:toggle');
                })
                .on('click', '.panel-actions a.fa-caret-down', function (e) {
                    e.preventDefault();
                    var $this = $(this);

                    $this
                            .removeClass('fa-caret-down')
                            .addClass('fa-caret-up');

                    $this.closest('.panel').trigger('panel:toggle');
                })
                .on('click', '.panel-actions a.fa-times', function (e) {
                    e.preventDefault();
                    var $this = $(this);

                    $this.closest('.panel').trigger('panel:dismiss');
                });
    });

})(jQuery);

//tooltips
$(function () {
    $('[data-toggle="tooltip"]').tooltip();
    $('[data-toggle="popover"]').popover()
});


//waves effects
  Waves.attach('.button-wave', ['waves-button', 'waves-light']);
            Waves.init();
}(window.jQuery);			
			