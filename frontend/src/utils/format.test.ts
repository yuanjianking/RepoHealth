import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  formatDate,
  formatRelativeTime,
  formatNumber,
  formatPercentage,
  formatDuration,
  formatFileSize,
  truncateText,
  getScoreColor,
  getSeverityColor,
  getDelayColor,
} from './format';

describe('format utilities', () => {
  describe('formatDate', () => {
    it('returns N/A for null or undefined', () => {
      expect(formatDate(null)).toBe('N/A');
      expect(formatDate(undefined)).toBe('N/A');
    });

    it('returns "Invalid date" for invalid date string', () => {
      expect(formatDate('invalid-date')).toBe('Invalid date');
    });

    it('formats valid date string', () => {
      const date = new Date('2026-04-03T10:30:00Z');
      const result = formatDate(date);
      expect(result).toMatch(/Apr 3, 2026.*10:30/);
    });

    it('formats ISO date string', () => {
      const result = formatDate('2026-04-03T10:30:00Z');
      expect(result).toMatch(/Apr 3, 2026.*10:30/);
    });
  });

  describe('formatRelativeTime', () => {
    beforeEach(() => {
      vi.useFakeTimers();
      vi.setSystemTime(new Date('2026-04-03T12:00:00Z'));
    });

    afterEach(() => {
      vi.useRealTimers();
    });

    it('returns "Just now" for recent time', () => {
      const date = new Date('2026-04-03T11:59:30Z');
      expect(formatRelativeTime(date)).toBe('Just now');
    });

    it('returns minutes ago', () => {
      const date = new Date('2026-04-03T11:30:00Z');
      expect(formatRelativeTime(date)).toBe('30 minutes ago');
    });

    it('returns hours ago', () => {
      const date = new Date('2026-04-03T08:00:00Z');
      expect(formatRelativeTime(date)).toBe('4 hours ago');
    });

    it('returns days ago', () => {
      const date = new Date('2026-04-01T12:00:00Z');
      expect(formatRelativeTime(date)).toBe('2 days ago');
    });

    it('returns weeks ago', () => {
      const date = new Date('2026-03-20T12:00:00Z');
      expect(formatRelativeTime(date)).toBe('2 weeks ago');
    });

    it('returns months ago', () => {
      const date = new Date('2026-01-15T12:00:00Z');
      expect(formatRelativeTime(date)).toBe('2 months ago');
    });
  });

  describe('formatNumber', () => {
    it('formats small numbers without commas', () => {
      expect(formatNumber(123)).toBe('123');
    });

    it('formats large numbers with commas', () => {
      expect(formatNumber(1234567)).toBe('1,234,567');
    });

    it('formats decimal numbers', () => {
      expect(formatNumber(1234.56)).toBe('1,234.56');
    });
  });

  describe('formatPercentage', () => {
    it('formats percentage with default decimal places', () => {
      expect(formatPercentage(85.123)).toBe('85.1%');
    });

    it('formats percentage with custom decimal places', () => {
      expect(formatPercentage(85.123, 2)).toBe('85.12%');
    });

    it('formats whole numbers correctly', () => {
      expect(formatPercentage(100)).toBe('100.0%');
    });
  });

  describe('formatDuration', () => {
    it('formats minutes less than 60', () => {
      expect(formatDuration(45)).toBe('45 mins');
      expect(formatDuration(1)).toBe('1 min');
    });

    it('formats hours without remaining minutes', () => {
      expect(formatDuration(120)).toBe('2 hrs');
      expect(formatDuration(60)).toBe('1 hr');
    });

    it('formats hours with remaining minutes', () => {
      expect(formatDuration(90)).toBe('1 hr 30 mins');
      expect(formatDuration(135)).toBe('2 hrs 15 mins');
    });
  });

  describe('formatFileSize', () => {
    it('returns 0 Bytes for 0', () => {
      expect(formatFileSize(0)).toBe('0 Bytes');
    });

    it('formats bytes', () => {
      expect(formatFileSize(500)).toBe('500 Bytes');
    });

    it('formats kilobytes', () => {
      expect(formatFileSize(2048)).toBe('2 KB');
      expect(formatFileSize(1536)).toBe('1.5 KB');
    });

    it('formats megabytes', () => {
      expect(formatFileSize(5 * 1024 * 1024)).toBe('5 MB');
    });

    it('formats gigabytes', () => {
      expect(formatFileSize(2.5 * 1024 * 1024 * 1024)).toBe('2.5 GB');
    });
  });

  describe('truncateText', () => {
    it('returns original text if within max length', () => {
      expect(truncateText('Hello World', 20)).toBe('Hello World');
    });

    it('truncates text with ellipsis if exceeds max length', () => {
      expect(truncateText('Hello World', 5)).toBe('Hello...');
    });

    it('handles empty string', () => {
      expect(truncateText('', 10)).toBe('');
    });
  });

  describe('getScoreColor', () => {
    it('returns green for scores >= 80', () => {
      expect(getScoreColor(80)).toBe('#4caf50');
      expect(getScoreColor(95)).toBe('#4caf50');
    });

    it('returns orange for scores >= 60 and < 80', () => {
      expect(getScoreColor(60)).toBe('#ff9800');
      expect(getScoreColor(75)).toBe('#ff9800');
    });

    it('returns red for scores < 60', () => {
      expect(getScoreColor(59)).toBe('#f44336');
      expect(getScoreColor(30)).toBe('#f44336');
    });
  });

  describe('getSeverityColor', () => {
    it('returns correct colors for severity levels', () => {
      expect(getSeverityColor('critical')).toBe('#d32f2f');
      expect(getSeverityColor('high')).toBe('#f44336');
      expect(getSeverityColor('medium')).toBe('#ff9800');
      expect(getSeverityColor('low')).toBe('#4caf50');
    });

    it('returns gray for unknown severity', () => {
      expect(getSeverityColor('unknown')).toBe('#9e9e9e');
      expect(getSeverityColor('')).toBe('#9e9e9e');
    });

    it('is case insensitive', () => {
      expect(getSeverityColor('CRITICAL')).toBe('#d32f2f');
      expect(getSeverityColor('High')).toBe('#f44336');
    });
  });

  describe('getDelayColor', () => {
    it('returns green for delay <= 10%', () => {
      expect(getDelayColor(0)).toBe('#4caf50');
      expect(getDelayColor(10)).toBe('#4caf50');
    });

    it('returns orange for delay <= 20%', () => {
      expect(getDelayColor(11)).toBe('#ff9800');
      expect(getDelayColor(20)).toBe('#ff9800');
    });

    it('returns red for delay > 20%', () => {
      expect(getDelayColor(21)).toBe('#f44336');
      expect(getDelayColor(50)).toBe('#f44336');
    });
  });
});
