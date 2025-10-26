export const NfeIcon = ({ size }) => {
  return (
    <svg
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 20 20"
      width={size}
      height={size}
    >
      <g clip-path="url(#a)">
        <path
          d="M7.3103 5.7432h5.3794M7.3103 8.9865h5.3794m-5.3794 3.2432h2.069M4.8276 17.5h10.3448c.4571 0 .8276-.363.8276-.8108V3.3108c0-.4478-.3705-.8108-.8276-.8108H4.8276C4.3706 2.5 4 2.863 4 3.3108v13.3784c0 .4478.3705.8108.8276.8108Z"
          stroke="#030712"
          stroke-width="1.1"
          stroke-linecap="square"
          stroke-linejoin="round"
        />
        <g clip-path="url(#b)">
          <mask
            id="c"
            style={{ maskType: "luminance" }}
            maskUnits="userSpaceOnUse"
            x="10"
            y="10"
            width="10"
            height="10"
          >
            <path
              d="M15 20c2.7614 0 5-2.2386 5-5s-2.2386-5-5-5-5 2.2386-5 5 2.2386 5 5 5Z"
              fill="#fff"
            />
          </mask>
          <g mask="url(#c)">
            <path d="M10 10h10v10H10V10Z" fill="#6DA544" />
            <path
              d="M15 11.957 19.1309 15 15 18.043 10.8691 15 15 11.957Z"
              fill="#FFDA44"
            />
            <path
              d="M13.4023 14.3164a1.7006 1.7006 0 0 0-.1406.709l3.1641.9726a1.7282 1.7282 0 0 0 .2812-.664c-.793-1.2754-2.3379-1.5684-3.3027-1.0156l-.002-.002Z"
              fill="#EEE"
            />
            <path
              d="M14.9941 13.2617a1.738 1.738 0 0 0-.8183.2071 1.7387 1.7387 0 0 0-.7735.8476 3.55 3.55 0 0 1 3.3028 1.0195 1.7383 1.7383 0 0 0-.1758-1.1601 1.7387 1.7387 0 0 0-1.5352-.9141Zm-.8535 1.6309a2.911 2.911 0 0 0-.8789.1328c.0033.2789.0736.5529.2051.7988a1.7388 1.7388 0 0 0 1.0312.8417 1.7394 1.7394 0 0 0 1.9239-.6678 2.9496 2.9496 0 0 0-2.2813-1.1055Z"
              fill="#0052B4"
            />
          </g>
        </g>
        <rect
          x="9.45"
          y="9.45"
          width="11.1"
          height="11.1"
          rx="5.55"
          stroke="#fff"
          stroke-width="1.1"
        />
      </g>
      <defs>
        <clipPath id="a">
          <path fill="#fff" d="M0 0h20v20H0z" />
        </clipPath>
        <clipPath id="b">
          <rect x="10" y="10" width="10" height="10" rx="5" fill="#fff" />
        </clipPath>
      </defs>
    </svg>
  );
};
