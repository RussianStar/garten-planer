import { differenceInCalendarDays, parseISO } from "../utils/dates";

type Props = {
  earliest: string;
  typical: string;
  latest: string;
};

const timelineWidth = 320; // px

export function RangeBar({ earliest, typical, latest }: Props) {
  const start = parseISO(earliest);
  const typ = parseISO(typical);
  const end = parseISO(latest);

  const totalDays = Math.max(differenceInCalendarDays(end, start), 1);
  const typicalOffset = differenceInCalendarDays(typ, start);

  const fullWidth = timelineWidth;
  const fuzzWidth = fullWidth;
  const mainWidth = Math.max((fullWidth * typicalOffset) / totalDays, 4);

  return (
    <div style={{ width: fullWidth, position: "relative", height: 18 }}>
      <div
        style={{
          position: "absolute",
          top: 6,
          left: 0,
          height: 6,
          width: fuzzWidth,
          background: "rgba(16, 112, 202, 0.18)",
          borderRadius: 4,
        }}
      />
      <div
        style={{
          position: "absolute",
          top: 3,
          left: 0,
          height: 12,
          width: mainWidth,
          background: "rgba(16, 112, 202, 0.55)",
          borderRadius: 4,
        }}
      />
      <div
        style={{
          position: "absolute",
          left: fuzzWidth + 6,
          top: 0,
          fontSize: 12,
          color: "#234",
        }}
      >
        {earliest} → {latest}
      </div>
    </div>
  );
}
