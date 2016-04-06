(function(exports) {
    "use strict";

    function parseKVX(kvx) {
        var lines = kvx.split('\n');

        var mov = {}
        mov.frames = [];
        var frame;

        function newFrame() {
            frame = {};
            frame.lines = [];
            mov.frames.push(frame);
        }

        lines.forEach(function(line) {
            var parts = line.split(' ');
            var cmd = parts.shift();

            if (cmd == 'CRD')
                mov.width = parts[0], mov.height = parts[1];
            else if (cmd == 'FRM')
                newFrame();
            else if (cmd == 'CUR')
                frame.cx = parts[0], frame.cy = parts[1];
            else if (cmd == 'COL')
                frame.col = 'rgb(' + [parts[2], parts[1], parts[0]].join(',') + ')';
            else if (cmd == 'CONT')
                frame.lines.push(parts);
        });

        return mov;
    }

    function playKVX(kvx) {
        var mov = parseKVX(kvx);

        var container = document.createElement('div');

        var canvas = document.createElement('canvas');
        canvas.width = mov.width;
        canvas.height = mov.height;
        container.appendChild(canvas);

        var cursor = document.createElement('img');
        cursor.src = 'cursor_1.png';
        cursor.style.position = 'absolute';
        container.appendChild(cursor);

        var ctx = canvas.getContext('2d');
        ctx.fillStyle = '#000';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        function drawFrame(frame) {
            cursor.style.left = frame.cx + 'px';
            cursor.style.top = frame.cy + 'px';

            ctx.strokeStyle = frame.col;
            ctx.lineWidth = 2;
            function drawLine(line) {
                ctx.moveTo(line[0], line[1]);
                for (var i = 2; i < line.length; i += 2)
                    ctx.lineTo(line[i], line[i+1]);
            }

            ctx.beginPath();
            frame.lines.forEach(drawLine);
            ctx.stroke();
        }

        var i = 0;
        function nf() {
            setTimeout(function() {
                for (var j = 5; j; j--)
                    drawFrame(mov.frames[i++]);
                if (i < mov.frames.length)
                    nf();
            }, 1);
        }
        nf();

        return container;
    }

    var req = new XMLHttpRequest();
    req.overrideMimeType('text/plain');
    req.open('GET', 'out.kvx', false);
    req.send();

    window.onload = function() {
        document.body.appendChild(playKVX(req.response));
    };

})(window);
