  const toogleBtn = document.querySelector('.navbar_toogleBtn');
  const menu = document.querySelector('.navbar_menu');
  const button = document.querySelector('.navbar_button');

  toogleBtn.addEventListener('click', () => {
    menu.classList.toogle('active');
    button.classList.toogle('active');
  });