import {refreshPresTree, route} from "./script.js";

const userSettingsBtn = document.querySelector('#user-settings-btn')
userSettingsBtn.addEventListener('click', async () => {
    userSettingsWrapper.classList.remove('hidden')
    await initSettingsFolders()
})

const userSettingsWrapper = document.querySelector('.user-settings-wrapper')
userSettingsWrapper.addEventListener('click', async () => {
    userSettingsWrapper.classList.add('hidden')
    await refreshPresTree()
})

const userSettingsModal = document.querySelector('.user-settings-modal')
userSettingsModal.addEventListener('click', (e) => {
    e.stopPropagation()
})

const userSettingsModalBody = document.querySelector('.user-settings-modal-body')

const userSettingsPath = document.querySelector('.user-settings-modal-path')


const initSettingsFolders = async () => {
    userSettingsPath.innerHTML = ''
    userSettingsModalBody.innerHTML = ''

    const roots = await fetch(route + 'folders/sync').then(res => res.json())
    await drawFolders(roots)

    const rootPathElement = document.createElement('div')
    rootPathElement.innerHTML = '://'
    rootPathElement.classList.add('user-settings-modal-path-element')
    userSettingsPath.appendChild(rootPathElement)

    rootPathElement.addEventListener('click', async () => {
        await drawFolders(roots)
        while (userSettingsPath.children.length > 1) {
            userSettingsPath.children[1].remove()
        }
    })
}



const drawFolders = async (folders) => {
    const preferences = await fetch(route + 'folders/mapped-list-pref').then(res => res.json())
    userSettingsModalBody.innerHTML = ''
    for (const folder of folders) {
        const folderObject = document.createElement('div')
        folderObject.classList.add('user-settings-modal-folder')
        userSettingsModalBody.appendChild(folderObject)

        const folderImg = document.createElement('img')
        folderImg.classList.add('user-settings-modal-folder-img')
        if (preferences[folder.id] === 1) {
            folderImg.src = '/views/icons/folder-full-pref.svg'
        } else if (preferences[folder.id] === 0) {
            folderImg.src = '/views/icons/folder-sub-pref.svg'
        } else {
            folderImg.src = '/views/icons/folder.svg'
        }
        folderObject.appendChild(folderImg)
        folderObject.folderImg = folderImg
        folderObject.innerHTML += folder.name

        folderObject.preferences = preferences

        folderObject.addEventListener('contextmenu', async (e) => {
            e.preventDefault()
            if (preferences[folder.id] === 1) {
                await fetch(route + 'folders/remove-pref?' + new URLSearchParams({
                    folder_id: folder.id
                }), {
                    method: 'POST'
                })
            } else {
                await fetch(route + 'folders/add-pref?' + new URLSearchParams({
                    folder_id: folder.id
                }), {
                    method: 'POST'
                })
            }
            await drawFolders(folders)
        })

        folderObject.addEventListener('dblclick', async () => {
            if (folder.children.length > 0) {
                await drawFolders(folder.children)

                const pathElement = document.createElement('div')
                pathElement.innerHTML = `${folder.name} /`
                pathElement.classList.add('user-settings-modal-path-element')
                const pathIndex = userSettingsPath.children.length
                userSettingsPath.appendChild(pathElement)

                pathElement.addEventListener('click', async () => {
                    await drawFolders(folder.children)
                    while (userSettingsPath.children.length > pathIndex + 1) {
                        userSettingsPath.children[pathIndex + 1].remove()
                    }
                })

            }

        })
    }
}

