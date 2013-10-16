$(document).ready(function() {
    // jQery object variables
    var $board = $('#board'),
        $dot   = '<div class="element dot"></div>';
                
    // Variables for holding dimensions of 'divs'
    var m = 5, d1 = 10, d2 = 50; 
    var bdim = (7*(m + d1 + m + d2) + m + d1 + m);
    
    // Varaibles for holding data about numbers and filled lines
    var numArray = Array(7);
    for (var i=0; i<7; i++) { numArray[i] = [-1, -1, -1, -1, -1, -1, -1]; }    
    var posNum = [-1,0,1,2,3];
    var boardLocked = false;
    
    var line = function(dir, y, x) {
        s = '<div class="element {0}-line line nd" id="{0}{1}-{2}"></div>';
        return s.replace(/\{0\}/g, dir).replace("{1}", y).replace("{2}", x); 
    }
    
    var entry = function(y, x) {
        s = '<div class="element entry" id="e{0}-{1}"></div>';
        return s.replace("{0}", y).replace("{1}", x);
    }
    
    var printH = function(y) {
        for (var i=0; i<7; i++) {
            $board.append($dot, line('h', y, 2*i+1));
        }
        $board.append($dot);
    }
    
    var printV = function(y) {
        for (var i=0; i<7; i++) {
            $board.append(line('v', y, 2*i), entry((y-1)/2, i));
        }
        $board.append(line('v', y, 2*7));
    }
    
    var refine = function(n) {
        if (n<0) {
            return n.toString();
        } else {
            return ' ' + n.toString();
        }
    }
    
    var parseURL = function() {
        var keyValPairs, keyVal, l,
            obj = {};
        keyValPairs = window.location.search.slice(1).split("&");
        for (var i=0; i<keyValPairs.length; i++) {
            keyVal = keyValPairs[i];
            l = keyVal.split("=");
            obj[l[0]] = l[1];
        }
        console.log(obj);
        return obj;
    }
    
    var init = function() {
        
        $board.css({width: bdim, height: bdim});
        //$board.css("backgroundColor", "pink");
        for (var j=0; j<7; j++) {
            printH(2*j);
            printV(2*j + 1);
        }
        printH(2*7);
        if (window.location.search) { // only if url-parameters are passed
            array = parseURL()['param']; //encoded array string
            array = decodeURIComponent(array)      //decoded array string
            numArray = eval(array);                //array
            console.log("Numeric Array via URL: ", numArray);
            config();
            if (parseURL()['lock'] === 'true') {
                boardLocked = true;
                console.log("Locked")
            }
        }
    }
    
    var config = function() { //update 'entry' elements as per numArray
        var n;
        for (var i=0; i<7; i++) {
            for (var j=0; j<7; j++) {
                n = numArray[i][j]
                if (n<0) { // -1 -> ''
                    n = "";
                } else {   //  x -> 'x' (0 <= x <= 4)
                    n = n.toString();
                }
                $('#e' + i + '-' + j).text(n)
            }
        }
    }
    
    init();
    
    $('.line').click(function() {
        $(this).toggleClass("dark nd");
    });
        
    $('.entry').click(function() {
        if (!boardLocked) {
            var s = (this.id).slice(1).split("-");  // id of form "e1-0"
            var y = parseInt(s[0]), x = parseInt(s[1]);
            var n = posNum.indexOf(numArray[y][x]);
            n = (n + 1) % 5;
            s = posNum[n]
            if (s!=(-1)) { 
                $(this).text(s);
            } else {
                $(this).text(' ');
            }
            numArray[y][x] = s;
        }
    });
    
    $('#panel').click(function() {
        s = "["
        for (var i=0; i<7; i++) {
            s += "["
            for (var j=0; j<7; j++) {
                s += refine(numArray[i][j])
                if (j!=6) {
                    s += ","
                }
            }
            s += "]"
            if (i!=6) {
                s += ",<br>&nbsp;"
            } else {
                s += "]"
            }
        }
        $('#text p').html(s)
    });
    
});      

    
    // pastebin api variables
    /*
    var key          = '4729cb33284750f5bd3714d120641b7e',
        paste_option = 'paste',
        paste_status = '1',
        paste_expire = '10M',
        paste_format = 'python',
        api_url      = 'http://pastebin.com/api/api_post.php';
    */


/*
    $.ajax({type    : "POST",
            url     : api_url,
            isLocal : true,
            data    : { api_dev_key      : key,
                        api_option       : paste_option,
                        api_paste_private: paste_status,
                        api_paste_expire : paste_expire,
                        api_paste_format : paste_format,
                        api_paste_code   : encodeURIComponent(numArray) },
            dataType: "text",
            success : function(data) {
                        alert("success");
                        console.log("Success\n" + data);
                      }, 
            error   : function(jqXHR, textStatus, errorThrown) {
                        alert(textStatus);
                        console.log("Error\n" + errorThrown);
                        console.log("jqXHR");
                        console.log(jqXHR);
                      },
            complete: function(jqXHR, textStatus) {
                        alert(textStatus);
                        console.log("Complete jqXHR");
                        console.log(jqXHR);
                      }
            .done(function(data) 
            {
                prompt("success");
                console.log("Success\n" + data);
            }
              });
              
        */
