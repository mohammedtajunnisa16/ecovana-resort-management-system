const revealItems = document.querySelectorAll(".property-card,.moment-card,.stats div");

const observer = new IntersectionObserver((entries)=>{
    entries.forEach(entry=>{
        if(entry.isIntersecting){
            entry.target.classList.add("show");
        }
    });
},{threshold:.15});

revealItems.forEach(item=>observer.observe(item));