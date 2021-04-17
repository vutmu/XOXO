

const socket = io(location.href)
//socket.on("connect", () => {
//  socket.emit("chat_message", "create game",);
//});
socket.on("connect", () => {
  socket.emit("chat_message", "get_visitors", (response) =>{
        $.each(response, render_visitor )
  });
});

socket.on("add_visitor", (data) =>{
    $.each(data, render_visitor )
});

function render_visitor(name, avatar){
    let visitorblock = `
                <div class="visitorblock" id=${name}>
                    ${name}<br>
                    <img src=${avatar} class="avka" alt="avatarka">
                </div>`;
    $('#visitors').append(visitorblock)
}

socket.on("del_visitor", (data) =>{
    let id='#'+data
    $(id).remove()
});

function field(field){
    field=field.field
    $("#grid-container>*").each(function(){
        let point=$(this).attr('id')
        let arr= point.split(',')
        let row=arr[0]
        let column=arr[1]
        let value=field[row][column]
        $(this).html(value)
    })
}

async function move() {
     return new Promise((resolve,reject)=>{
        $("#grid-container>*").on('click',function() {
            let point={point:$(this).attr('id')}
            resolve(point)
            })
        }
    )}

//это типо коекак работает?..
//async function move() {
//     return new Promise((resolve,reject)=>{
//        $("#grid-container>*").on('click',function() {
//            let point={point:$(this).attr('id')}
//            console.log("move запущен", point)
//
//            resolve(()=>{
//
//	            console.log(point)
//            })
//        })
//        }
//    )}

//    await $("#grid-container>*").on('click',function() {
//  if ($(this).text()=='') {
//  	console.log($(this).attr('id'))
//  	let point={point:$(this).attr('id')}
//	console.log(point)
//	return point
//	}
//  else {
//    return('клетка не пуста!')
//  }
//})
socket.on("set_field", (data) => {
    field(data)
})

socket.on("game_message", (data) => {
    $('#game_message').html(data.message)
})

socket.on("xoxo", async (data, callback) => {
    await callback(await move())
})