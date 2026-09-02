export default async function run(page, ui) {
  const out = {};
  await page.setViewportSize({ width: 1400, height: 900 });
  await page.waitForSelector('input[type=email]', { timeout: 15000 });
  await page.screenshot({ path: 'D:/Laboratorio/Python/Aplicaciones/Evaluacion_de_costos/screenshot_theme_login.png' });

  await page.fill('input[type=email]', 'admin@laboratorio.com');
  await page.fill('input[type=password]', 'admin123');
  await page.click('button[type=submit]');
  await page.waitForURL(/\/$/, { timeout: 15000 });
  await page.waitForSelector('canvas', { timeout: 15000 });
  await page.waitForTimeout(1200);
  out.bodyBg = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
  await page.screenshot({ path: 'D:/Laboratorio/Python/Aplicaciones/Evaluacion_de_costos/screenshot_theme_dashboard.png' });

  await page.goto('http://localhost:5174/determinaciones');
  await page.waitForSelector('.p-datatable', { timeout: 15000 });
  await page.waitForTimeout(800);
  await page.screenshot({ path: 'D:/Laboratorio/Python/Aplicaciones/Evaluacion_de_costos/screenshot_theme_determinaciones.png' });

  // Abrir diálogo de edición del primer registro
  const editBtn = page.locator('button[title*="Editar"], button:has(.pi-pencil)').first();
  if (await editBtn.count()) {
    await editBtn.click();
    await page.waitForSelector('.p-dialog', { timeout: 8000 });
    await page.waitForTimeout(600);
    await page.screenshot({ path: 'D:/Laboratorio/Python/Aplicaciones/Evaluacion_de_costos/screenshot_theme_dialog.png' });
    out.dialogOpened = true;
  }
  return out;
}
