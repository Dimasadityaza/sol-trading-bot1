/**
 * Secure storage utility for remember password feature
 * Uses browser's localStorage with basic obfuscation (NOT encryption)
 *
 * WARNING: This is NOT completely secure - anyone with access to browser can retrieve it
 * Only use for convenience, not for large amounts of funds
 */

const STORAGE_KEY = 'sol_sniper_pwd';

export const storage = {
  /**
   * Save password to localStorage (obfuscated)
   */
  savePassword: (password: string): void => {
    try {
      // Simple base64 obfuscation (NOT encryption!)
      const obfuscated = btoa(password);
      localStorage.setItem(STORAGE_KEY, obfuscated);
    } catch (error) {
      console.error('Failed to save password:', error);
    }
  },

  /**
   * Retrieve password from localStorage
   */
  getPassword: (): string | null => {
    try {
      const obfuscated = localStorage.getItem(STORAGE_KEY);
      if (!obfuscated) return null;

      // Decode base64
      return atob(obfuscated);
    } catch (error) {
      console.error('Failed to retrieve password:', error);
      return null;
    }
  },

  /**
   * Remove password from localStorage
   */
  clearPassword: (): void => {
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (error) {
      console.error('Failed to clear password:', error);
    }
  },

  /**
   * Check if password is saved
   */
  hasPassword: (): boolean => {
    return localStorage.getItem(STORAGE_KEY) !== null;
  }
};
