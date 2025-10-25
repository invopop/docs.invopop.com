export const SvgComponent = ({size}) => {
  return (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    fill="none"
    viewBox="0 0 20 20"
    width={size}
    height={size}
  >
    <path fill="#C92D45" d="M3 10h15v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-7Z" />
    <path fill="#E5E7EB" d="M3 3a2 2 0 0 1 2-2h9l2 2 2 2v5H3V3Z" />
    <g filter="url(#a)">
      <path fill="#000" fillOpacity={0.19} d="m13 6 1-5 4 4-5 1Z" />
    </g>
    <path fill="#D9D9D9" d="M14 5V1l4 4h-4Z" />
    <path
      fill="#F9FAFB"
      d="M6.062 14.262h.472c.211 0 .38-.06.509-.182.132-.121.199-.31.199-.567 0-.252-.057-.444-.17-.575-.113-.13-.302-.196-.568-.196h-.442v1.52ZM5 12h1.858c.27 0 .497.044.679.133a1.195 1.195 0 0 1 .693.82c.049.177.073.359.073.546 0 .256-.041.48-.125.672a1.172 1.172 0 0 1-.34.47 1.41 1.41 0 0 1-.523.272c-.206.06-.435.091-.685.091h-.568V17H5v-5Zm4.937 4.258h.472c.187 0 .337-.03.45-.091a.617.617 0 0 0 .265-.302c.07-.14.113-.324.133-.553.025-.228.037-.513.037-.854 0-.285-.01-.535-.03-.75a1.653 1.653 0 0 0-.125-.531.63.63 0 0 0-.273-.323c-.118-.074-.277-.112-.48-.112h-.449v3.516ZM8.875 12h1.74c.37 0 .667.058.893.175.226.112.4.275.523.49.128.21.214.465.258.764.045.298.067.632.067 1.001 0 .439-.03.822-.089 1.148-.054.323-.15.589-.287.799a1.26 1.26 0 0 1-.553.469c-.231.103-.524.154-.878.154H8.875v-5Zm4.183 0H16v.826h-1.88v1.177h1.77v.826h-1.77V17h-1.062v-5Z"
    />
    <defs>
      <filter
        id="a"
        width={6}
        height={6}
        x={12.5}
        y={0.5}
        colorInterpolationFilters="sRGB"
        filterUnits="userSpaceOnUse"
      >
        <feFlood floodOpacity={0} result="BackgroundImageFix" />
        <feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape" />
        <feGaussianBlur
          result="effect1_foregroundBlur_1271_102"
          stdDeviation={0.25}
        />
      </filter>
    </defs>
  </svg>
  )
}