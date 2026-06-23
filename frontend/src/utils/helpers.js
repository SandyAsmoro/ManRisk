// ...\ManRiskMSKI\frontend\src\utils\helpers.js

export const QUARTER_MONTHS = {
  Q1: [1, 2, 3],    // Januari–Maret
  Q2: [4, 5, 6],    // April–Juni
  Q3: [7, 8, 9],    // Juli–September
  Q4: [10, 11, 12], // Oktober–Desember
};

/**
 * Mengecek apakah kuartal tertentu sedang terbuka untuk input/edit
 * berdasarkan bulan berjalan di sistem/browser saat ini.
 * @param {string} quarter - Contoh: "Q1", "Q2"
 * @returns {boolean} - true jika boleh diedit, false jika terkunci
 */
export function isQuarterEditable(quarter) {
  if (!QUARTER_MONTHS[quarter]) return false;
  
  const currentMonth = new Date().getMonth() + 1; // getMonth() mulai dari 0 (Jan) - 11 (Des)
  return QUARTER_MONTHS[quarter].includes(currentMonth);
}