import { join } from 'node:path';
import type { AboutPanelOptionsOptions, App, MenuItemConstructorOptions } from 'electron';
import { PRODUCT_NAME } from '../../../config/app-config.mjs';

export const DESKTOP_APP_NAME = PRODUCT_NAME;

/**
 * Electron's userData folder name from before the Arplio Voice rename. It holds
 * the Python runtime, runtime preferences and crash journals, so it stays fixed
 * while the visible product name changes; renaming it orphans that state.
 */
export const USER_DATA_DIR_NAME = 'VoiceStudio';

/** Set before Electron creates the native application menu or reads userData. */
export function installAppIdentity(
  application: Pick<App, 'setName' | 'getPath' | 'setPath'>,
): void {
  application.setName(DESKTOP_APP_NAME);
  application.setPath('userData', join(application.getPath('appData'), USER_DATA_DIR_NAME));
}

export function createMacApplicationMenuTemplate(): MenuItemConstructorOptions[] {
  return [
    {
      label: DESKTOP_APP_NAME,
      submenu: [
        { role: 'about' },
        { type: 'separator' },
        { role: 'services' },
        { type: 'separator' },
        { role: 'hide' },
        { role: 'hideOthers' },
        { role: 'unhide' },
        { type: 'separator' },
        { role: 'quit' },
      ],
    },
    { role: 'fileMenu' },
    { role: 'editMenu' },
    { role: 'viewMenu' },
    { role: 'windowMenu' },
  ];
}

interface AboutApplication {
  setAboutPanelOptions(options: AboutPanelOptionsOptions): void;
}

interface ApplicationMenuInstaller<TMenu> {
  buildFromTemplate(template: MenuItemConstructorOptions[]): TMenu;
  setApplicationMenu(menu: TMenu): void;
}

export function installMacApplicationMenu<TMenu>(
  application: AboutApplication,
  menu: ApplicationMenuInstaller<TMenu>,
  version: string,
): void {
  application.setAboutPanelOptions({
    applicationName: DESKTOP_APP_NAME,
    applicationVersion: version,
    version,
  });
  menu.setApplicationMenu(menu.buildFromTemplate(createMacApplicationMenuTemplate()));
}
