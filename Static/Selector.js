// The function which sets up selector in the frontend
$(document).ready(function() {
    $("#dropdown").select2({
        placeholder: "Choose your favourite book...",
        allowClear: true,
        ajax: {
            url: "/get-options",
            dataType: "json",
            delay: 250,
            data: function(params) {
                return {
                    term: params.term || ""
                };
            },
            processResults: function(data) {
                return {
                    results: data.map(item => ({
                        id: item["ISBN"],
                        text: item["Book-Title"]
                    }))
                };
            }
        }
    });
    // The function which displays recommended books
    function renderBooks(bookList){
                    console.log(bookList)
                    const bookListContainer = document.getElementById("book-list");
                    bookListContainer.innerHTML = "";
                    bookList.forEach(book => {
                const bookElement = document.createElement("div");
                bookElement.classList.add("book");
                bookElement.innerHTML = `
                    <img src="${book["Image-URL-L"]}" alt="${book.book}">
                    <div class="book-info">
                        <div class="book-title">${book["book"]}</div>
                        <div class="book-author-">${book["Book-Author"]} </div>
                       
                        
              
                    </div>
                `;
                bookListContainer.appendChild(bookElement);
            });
                }
    // Button setup, it sends the data to backend, gets the list of recommended books and than calls the function for rendering

    $("#Sent").click(function() {
        const element1 = document.querySelector('.container');
        element1.style.visibility = 'visible';
        var inputValue = $("#dropdown").val();
        console.log(inputValue)
        $.ajax({
            url: "/sent-data",
            type: "POST",
            dataType: "json",
            delay: 250,
            contentType: "application/json",
            data: JSON.stringify({
        ISBN: String(inputValue)

    }),
            success: function(response) {

            console.log("Data was sent successfully:", response);

            if (response.status === "success") {
                let books = response.rec_books;
                renderBooks(books);
                console.log("The function was successful:", response.rec_books);
            } else {
                console.error("Error: API didn´t return correct data", response);
            }
        },
        error: function(xhr, status, error) {
            console.error("Error while sending the data:", error);
        }
        });
    });
});
