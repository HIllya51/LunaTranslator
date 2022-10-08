var page=require('webpage').create();

page.open('http://cuiqingcai.com',function(status){

    console.log("Status: "+status);

    if(status==="success"){

        page.render('example.png');

    }

    phantom.exit();

});