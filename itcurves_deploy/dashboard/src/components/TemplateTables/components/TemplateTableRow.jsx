import { TableRow, TableCell, Typography, Chip, IconButton } from "@mui/material";
import DeleteIcon from '../../../assets/DeleteRow.svg';
import CloneIcon from '../../../assets/Clone.svg';
import LaunchSurvey from '../../../assets/LaunchSurvey.svg';

const TemplateTableRow = ({ 
  template, 
  onTemplateClick, 
  onDeleteClick, 
  onCloneClick, 
  onLaunchSurveyClick 
}) => {
  return (
    <TableRow
      key={template.id}
      hover
      onClick={() => onTemplateClick(template)}
      sx={{
        height: "48px",
        "& td": {
          height: "48px",
          minHeight: "48px",
          maxHeight: "48px",
          paddingTop: "8px",
          paddingBottom: "8px",
          fontFamily: "Poppins, sans-serif",
          fontWeight: 400,
          fontSize: "14px",
          lineHeight: "100%",
          color: "#4B4B4B",
          cursor: 'pointer',
          borderBottom: "1px solid #F0F0F0",
        },
      }}
    >
      <TableCell>{template.id}</TableCell>
      <TableCell>
        <Typography
          sx={{
            cursor: 'pointer',
            fontFamily: 'Poppins, sans-serif',
            fontWeight: 400,
            fontSize: '14px',
          }}  
        >
          {template.name}
        </Typography>
      </TableCell>
      <TableCell>{template.formattedDate}</TableCell>
      <TableCell>
        <Chip
          label={template.status}
          sx={{
            backgroundColor:
              template.status === "Published"
                ? "#E4FFEA"
                : "#F3F3FF",
            color:
              template.status === "Published"
                ? "#00A857"
                : "#550FEC",
            fontWeight: 500,
            fontFamily: "Poppins, sans-serif",
            borderRadius: "6px",
            fontSize: "13px",
            height: "30px",
          }}
        />
      </TableCell>
      <TableCell align="right">
        {template.status === "Published" && (
          <IconButton
            variant="outlined"
            sx={{
              mr: 1,
              width: "162px",
              borderRadius: "15px",
              height: "40px",
            }}
            onClick={(e) => onLaunchSurveyClick(e, template)}
          >
            <img src={LaunchSurvey} alt="Launch Survey" />
          </IconButton>
        )}
        {template.status == "Published" && 
          <IconButton
            variant="outlined"
            onClick={(e) => onCloneClick(e, template)}
            sx={{
              borderRadius: "15px",
              width: "100px",
              height: "40px",
              mr: 1,
            }}
          >
            <img src={CloneIcon} alt="Clone" />
          </IconButton>
        }
        {template.status !== "Published" && (
          <IconButton
            variant="outlined"
            onClick={(e) => onDeleteClick(e, template)}
            sx={{
              borderRadius: "15px",
              width: "100px",
              height: "40px",
            }}
          >
            <img src={DeleteIcon} alt="Delete" />
          </IconButton>
        )}
      </TableCell>
    </TableRow>
  );
};

export default TemplateTableRow;
