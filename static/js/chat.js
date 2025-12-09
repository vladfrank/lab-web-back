document.getElementById("send-form").addEventListener("submit", async function(e){
    e.preventDefault(); // Отменяем стандартное поведение формы (перезагрузку страницы)
    
    const receiver_id = document.getElementById("receiver_id").value; // ID получателя
    const text = document.getElementById("msg-text").value;           // Текст сообщения
    if(!text) return; // Если текст пустой - ничего не делаем

    // Отправка POST-запроса на сервер
    const res = await fetch("/messenger/send", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: `receiver_id=${receiver_id}&text=${encodeURIComponent(text)}`
    });

    if(res.ok){
        location.reload(); // Если всё успешно - перезагружаем страницу, чтобы показать новое сообщение
    }
});

function deleteMessage(id){
    fetch(`/messenger/delete_message/${id}`, { method: "POST"})
        .then(r => r.ok ? location.reload() : alert("Ошибка удаления"));
}
