/**
 * Funções JavaScript para o site da Pousada Pajéu
 */
document.addEventListener('DOMContentLoaded', function() {
    // Inicializa tooltips do Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Inicializa popovers do Bootstrap
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Smooth scroll para links de âncora
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            
            if (targetId !== '#') {
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    window.scrollTo({
                        top: targetElement.offsetTop - 70,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });

    // Adiciona classe active ao link do navbar conforme a seção visível
    window.addEventListener('scroll', function() {
        const sections = document.querySelectorAll('section[id]');
        const scrollY = window.pageYOffset;
        
        sections.forEach(section => {
            const sectionHeight = section.offsetHeight;
            const sectionTop = section.offsetTop - 100;
            const sectionId = section.getAttribute('id');
            
            if (scrollY > sectionTop && scrollY <= sectionTop + sectionHeight) {
                document.querySelector('.navbar-nav a[href*=' + sectionId + ']')?.classList.add('active');
            } else {
                document.querySelector('.navbar-nav a[href*=' + sectionId + ']')?.classList.remove('active');
            }
        });
    });

    // Validação de formulários
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });

    // Contador de caracteres para textarea
    const textareas = document.querySelectorAll('textarea[maxlength]');
    
    textareas.forEach(textarea => {
        const maxLength = textarea.getAttribute('maxlength');
        const counterEl = document.createElement('div');
        counterEl.className = 'char-counter text-end text-muted small mt-1';
        counterEl.innerHTML = `0/${maxLength} caracteres`;
        
        textarea.parentNode.insertBefore(counterEl, textarea.nextSibling);
        
        textarea.addEventListener('input', function() {
            const currentLength = this.value.length;
            counterEl.innerHTML = `${currentLength}/${maxLength} caracteres`;
            
            if (currentLength > maxLength * 0.9) {
                counterEl.classList.add('text-danger');
            } else {
                counterEl.classList.remove('text-danger');
            }
        });
    });

    // Máscaras para campos de formulário
    const telefoneInputs = document.querySelectorAll('.telefone-mask');
    telefoneInputs.forEach(input => {
        input.addEventListener('input', function() {
            let value = this.value.replace(/\D/g, '');
            
            if (value.length > 11) {
                value = value.substring(0, 11);
            }
            
            if (value.length > 7) {
                this.value = value.replace(/^(\d{2})(\d{5})(.*)/, '($1) $2-$3');
            } else if (value.length > 2) {
                this.value = value.replace(/^(\d{2})(.*)/, '($1) $2');
            } else {
                this.value = value;
            }
        });
    });

    // Cálculo dinâmico de preços na página de reservas
    const calculaPrecoReserva = () => {
        const checkIn = document.getElementById('check_in');
        const checkOut = document.getElementById('check_out');
        const adultos = document.getElementById('adultos');
        const criancas = document.getElementById('criancas');
        const quartoSelect = document.getElementById('quarto');
        const totalElement = document.getElementById('preco_total');
        
        if (checkIn && checkOut && adultos && totalElement && quartoSelect) {
            const dataCheckIn = new Date(checkIn.value);
            const dataCheckOut = new Date(checkOut.value);
            
            if (dataCheckIn && dataCheckOut && !isNaN(dataCheckIn) && !isNaN(dataCheckOut)) {
                const diffTime = Math.abs(dataCheckOut - dataCheckIn);
                const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                
                const quartoOption = quartoSelect.options[quartoSelect.selectedIndex];
                const precoBase = quartoOption ? parseFloat(quartoOption.getAttribute('data-preco') || 0) : 0;
                
                const numAdultos = parseInt(adultos.value) || 0;
                const numCriancas = parseInt(criancas?.value) || 0;
                
                // Taxa adicional por pessoa extra
                const pessoasIncluidas = parseInt(quartoOption?.getAttribute('data-capacidade') || 2);
                const pessoasExtras = Math.max(0, numAdultos + numCriancas - pessoasIncluidas);
                const taxaExtra = pessoasExtras * 50; // R$ 50 por pessoa extra
                
                const precoTotal = (precoBase + taxaExtra) * diffDays;
                
                if (precoTotal > 0 && diffDays > 0) {
                    totalElement.textContent = `R$ ${precoTotal.toFixed(2)}`;
                    document.getElementById('resumo_reserva')?.classList.remove('d-none');
                } else {
                    totalElement.textContent = 'R$ 0,00';
                    document.getElementById('resumo_reserva')?.classList.add('d-none');
                }
            }
        }
    };
    
    // Adiciona listeners para os campos de reserva
    ['check_in', 'check_out', 'adultos', 'criancas', 'quarto'].forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('change', calculaPrecoReserva);
        }
    });
    
    // Inicializa o cálculo
    calculaPrecoReserva();
}); 