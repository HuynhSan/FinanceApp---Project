// document.addEventListener('DOMContentLoaded', function() {
//     var accountBtn = document.getElementById("account-btn");
//     var dropdownMenu = document.getElementById("dropdown-menu");

//     if (accountBtn && dropdownMenu) {
//         accountBtn.addEventListener("click", function(event) {
//             // Ngăn sự kiện mặc định của thẻ <a> hoặc các thẻ liên quan đến link
//             event.preventDefault();
//             dropdownMenu.classList.toggle("hidden");
//         });
//     }
// });




// document.addEventListener('DOMContentLoaded', function() {
//     // Lắng nghe sự kiện click vào nút dropdown
//     document.getElementById('account-btn').addEventListener('click', function (event) {
//         event.preventDefault();  // Ngăn chặn hành động mặc định của liên kết
//         const menu = document.getElementById('dropdown-menu');
//         menu.classList.toggle('hidden');  // Toggle giữa hiển thị/ẩn menu
//     });

//     // Đảm bảo menu dropdown ẩn khi nhấp ra ngoài
//     document.addEventListener('click', function (event) {
//         const menu = document.getElementById('dropdown-menu');
//         const accountBtn = document.getElementById('account-btn');

//         if (!accountBtn.contains(event.target) && !menu.contains(event.target)) {
//             menu.classList.add('hidden');  // Ẩn menu khi nhấp ra ngoài
//         }
//     });
// });


document.addEventListener('DOMContentLoaded', function () {
    // Lấy các phần tử cần thiết
    const accountBtn = document.getElementById('account-btn');
    const dropdownMenu = document.getElementById('dropdown-menu');

    // Gán sự kiện click vào nút
    accountBtn.addEventListener('click', function (event) {
        event.stopPropagation();  // Ngừng sự kiện click tiếp tục (nghĩa là không lan ra ngoài)

        // Chuyển trạng thái hiển thị của dropdown
        dropdownMenu.classList.toggle('hidden');
    });

    // Ẩn dropdown nếu người dùng nhấp ra ngoài
    document.addEventListener('click', function (event) {
        if (!accountBtn.contains(event.target) && !dropdownMenu.contains(event.target)) {
            dropdownMenu.classList.add('hidden');
        }
    });
});



document.addEventListener("DOMContentLoaded", function () {
    const toggleBtn = document.getElementById("menu-toggle");
    const mobileMenu = document.getElementById("mobile-menu");

    toggleBtn.addEventListener("click", function () {
        mobileMenu.classList.toggle("hidden");
    });
});



