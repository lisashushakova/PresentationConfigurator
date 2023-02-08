import {route} from "./script.js";

export default function initSlideSearch(drawerElement, presDrawer) {
    const slideSearchField = document.querySelector('.pres-drawer-search-field')
    const tagSearchBtn = document.querySelector('#pres-drawer-tag-search-btn')
    const textSearchBtn = document.querySelector('#pres-drawer-text-search-btn')

    const mainPresColumnHeader = document.querySelector('.main-pres-column-header')

    tagSearchBtn.addEventListener('click', async () => {
        const slidesFound = await fetch(route + 'slides/by-tag-query?' + new URLSearchParams({
            query: slideSearchField.value
        })).then(res => res.json())
        mainPresColumnHeader.innerHTML = 'Результаты поиска по тегам'
        await presDrawer.draw(drawerElement, slidesFound)

    })

    textSearchBtn.addEventListener('click', async () => {
        const slidesFound = await fetch(route + 'slides/by-text?' + new URLSearchParams({
            search_phrase: slideSearchField.value
        })).then(res => res.json())
        mainPresColumnHeader.innerHTML = 'Результаты поиска по тексту'
        await presDrawer.draw(drawerElement, slidesFound)
    })
}

