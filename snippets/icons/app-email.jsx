export const EmailIcon = ({ size }) => {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 20 20"
      width={size}
      height={size}
    >
      <g clipPath="url(#a)">
        <g clipPath="url(#b)">
          <rect
            width={19.091}
            height={12.409}
            x={0.477}
            y={3.773}
            fill="#D9D9D9"
            rx={2.864}
          />
          <mask
            id="d"
            width={20}
            height={14}
            x={0}
            y={3}
            maskUnits="userSpaceOnUse"
            style={{
              maskType: "alpha",
            }}
          >
            <rect
              width={19.091}
              height={12.409}
              x={0.477}
              y={3.773}
              fill="#D9D9D9"
              rx={2.864}
            />
          </mask>
          <g filter="url(#c)" mask="url(#d)">
            <path
              fill="#E5E7EB"
              d="M8.92 9.837-1.909 3.773h25.296L11.152 9.889a2.386 2.386 0 0 1-2.233-.052Z"
            />
          </g>
        </g>
      </g>
      <defs>
        <clipPath id="a">
          <path fill="#fff" d="M0 0h20v20H0z" />
        </clipPath>
        <clipPath id="b">
          <rect width={20} height={20} y={-1} fill="#fff" rx={2.727} />
        </clipPath>
        <filter
          id="c"
          width={29.114}
          height={10.187}
          x={-3.341}
          y={2.818}
          colorInterpolationFilters="sRGB"
          filterUnits="userSpaceOnUse"
        >
          <feFlood floodOpacity={0} result="BackgroundImageFix" />
          <feColorMatrix
            in="SourceAlpha"
            result="hardAlpha"
            values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0"
          />
          <feOffset dx={0.477} dy={0.955} />
          <feGaussianBlur stdDeviation={0.955} />
          <feComposite in2="hardAlpha" operator="out" />
          <feColorMatrix values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.19 0" />
          <feBlend
            in2="BackgroundImageFix"
            result="effect1_dropShadow_1121_42"
          />
          <feBlend
            in="SourceGraphic"
            in2="effect1_dropShadow_1121_42"
            result="shape"
          />
        </filter>
      </defs>
    </svg>
  );
};
