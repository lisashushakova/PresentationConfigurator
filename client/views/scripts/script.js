import PresentationDrawer from "./presentation-drawer.js";
import FilesTreeList from "./files-tree-list.js";
import initSlideSearch from "./slides-search.js";
import PresBuilder from "./pres-builder.js";


// export const route = 'https://pres-configurator.ru/'
export const route = 'http://localhost:8000/'

const [user_name, user_picture_url] = await fetch(route + 'auth/user-info').then(res => res.json())

const userIconImg = document.querySelector('#user-icon-img')
userIconImg.src = user_picture_url

const userNameBox = document.querySelector('#user-name-box')
userNameBox.innerHTML = user_name

const logoutBtn = document.querySelector('#logout-btn')
logoutBtn.addEventListener('click', async () => {
    location.href = route + 'auth/login'
})




const drawerElement = document.querySelector('.pres-drawer')
const presDrawer = new PresentationDrawer()

const ftlContainer = document.querySelector('#filesTreeList')
const ftl = new FilesTreeList(ftlContainer, async (presSlidesList) => {
    await presDrawer.draw(drawerElement, presSlidesList)
})



const syncDoneEvent = new CustomEvent('sync-done')


const refreshPresTree = async () => {
    const presTree = await fetch(route + 'presentations/tree').then(res => res.json())
    ftl.init(presTree)

    fetch(route + 'presentations/sync', {method: 'POST'}).then(() => {
        ftlContainer.dispatchEvent(syncDoneEvent)
    })

    const syncFilesTreeList = async () => {
        const statusList = await fetch(route + 'presentations/sync-status').then(res => res.json())
        ftl.updateSyncStatus(statusList)
    }

    const syncTimerId = setInterval(syncFilesTreeList, 2000)

    ftlContainer.addEventListener('sync-done', () => {
        clearInterval(syncTimerId)
        syncFilesTreeList()
    })

}
initSlideSearch(drawerElement, presDrawer)


const ftlRefreshBtn = document.querySelector('#ftl-refresh-btn')
ftlRefreshBtn.addEventListener('click', refreshPresTree)
await refreshPresTree()


const presBuilder = new PresBuilder()
presBuilder.init()

const exportAllSlidesBtn = document.querySelector('#export-all-slides-btn')
exportAllSlidesBtn.addEventListener('click', () => {
    presBuilder.addSlides(presDrawer.slides)
})

const exportSelectedSlidesBtn = document.querySelector('#export-selected-slides-btn')
exportSelectedSlidesBtn.addEventListener('click', () => {
    presBuilder.addSlides(presDrawer.selectedSlides)
})



