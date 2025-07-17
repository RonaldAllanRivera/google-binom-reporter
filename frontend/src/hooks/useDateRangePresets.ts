import dayjs, { Dayjs } from 'dayjs';
import { Dispatch, SetStateAction } from 'react';

type DateRangePreset = 'last7days' | 'last30days' | 'thisMonth' | 'lastMonth';

export const useDateRangePresets = (
  setStartDate: Dispatch<SetStateAction<Dayjs | null>>,
  setEndDate: Dispatch<SetStateAction<Dayjs | null>>
) => {
  const handleSetDateRange = (range: DateRangePreset) => {
    const today = dayjs();
    let start: Dayjs = today;
    let end: Dayjs = today;

    switch (range) {
      case 'last7days':
        start = today.subtract(7, 'day');
        break;
      case 'last30days':
        start = today.subtract(30, 'day');
        break;
      case 'thisMonth':
        start = today.startOf('month');
        break;
      case 'lastMonth':
        start = today.subtract(1, 'month').startOf('month');
        end = today.subtract(1, 'month').endOf('month');
        break;
    }
    setStartDate(start);
    setEndDate(end);
  };

  return { handleSetDateRange };
};
